from datetime import datetime
import numpy as np
from scipy.io import readsav
# from scipy.interpolate import splrep, splev
from scipy.interpolate import interp1d


def get_time_tai(date_string):
    # get the current time in TAI - specific for IDL.

    # IDL reference epoch: January 1, 1979, 00:00:00
    idl_ref_epoch = datetime(1979, 1, 1)

    # Unix epoch: January 1, 1970, 00:00:00
    unix_epoch = datetime(1970, 1, 1)

    # Calculate the difference in seconds between the IDL reference epoch and the Unix epoch
    epoch_diff = (idl_ref_epoch - unix_epoch).total_seconds()

    date_object = datetime.fromisoformat(date_string)
    unix_timestamp = date_object.timestamp()

    # Adjust the Unix timestamp by subtracting the epoch difference
    idl_timestamp = unix_timestamp - epoch_diff+3600

    return idl_timestamp

def read_calib_file():
    from scipy.io import readsav

    # Read the calibration file
    calib_file = readsav('eis_calibration/eis_calib_warren_2014.sav')
    return calib_file['eis']

def eis_get_band(wave):
    # get band based on the wavelength
    band = ''
    sw_min = 165
    sw_max = 213
    pShort = (wave - sw_min) * (sw_max - wave)
    if pShort >= 0:
        band = 'SW'

    lw_min = 245
    lw_max = 292
    pLong = (wave - lw_min) * (lw_max - wave)
    if pLong >= 0:
        band = 'LW'

    return band

from scipy.interpolate import interp1d

def eis_ea_nrl(date, wave, short=False, long=False):
    eis = read_calib_file()
    t = (get_time_tai(date) - get_time_tai(eis['t0'][0].decode('utf-8')))/(86400*365.25)
    ea_knots_SW = eis['a0_sw'][0]*np.exp(-t/eis['tau_sw'][0])
    ea_knots_LW = eis['a0_lw'][0]*np.exp(-t/eis['tau_lw'][0])

    # -----------------------------------------------------------------
    # --- return the effective area on a default wavelength grid
    if short:
        wave = eis['wave_area_sw'][0]
    elif long:
        wave = eis['wave_area_lw'][0]

    # -----------------------------------------------------------------
    # --- interpolate onto the input wavelength grid
    if isinstance(wave, (int, float)):
        wave = np.array([wave])

    nWave = len(wave)
    ea_out = np.zeros(nWave)

    for i in range(nWave):
        band = eis_get_band(wave[i])
        if band == 'SW':
            w = eis['wave_knots_sw'][0]
            e = np.log(ea_knots_SW)
            s = 1
        elif band == 'LW':
            w = eis['wave_knots_lw'][0]
            e = np.log(ea_knots_LW)
            s = 1
        else:
            print(f"WAVELENGTH OUT OF BOUNDS {wave[i]}")
            s = 0

        if s == 1:
            interp_func = interp1d(w, e, kind='linear')
            ea_out[i] = np.exp(interp_func(wave[i]))
        else:
            ea_out[i] = 0.0

    if nWave == 1:
        ea_out = ea_out[0]

    return ea_out
    
def eis_ea(input_wave, short=False, long=False):
    if short:
        wave, ea = eis_effective_area_read(short=True)
        input_wave = wave
        print(input_wave)
        return ea

    if long:
        wave, ea = eis_effective_area_read(long=True)
        input_wave = wave
        return ea
    if isinstance(input_wave, (int, float)):
        input_wave = np.array([input_wave])

    nWave = len(input_wave)
    ea = np.zeros(nWave)

    for i in range(nWave):
        short, long = is_eis_wavelength(input_wave[i])

        if not short and not long:
            ea[i] = 0.0
        else:
            wave, area = eis_effective_area_read(long=long, short=short)
            ea[i] = np.exp(np.interp(input_wave[i], wave, np.log(area)))

    if nWave == 1:
        ea = ea[0]

    return ea

def eis_effective_area_read(short=False, long=False):
    if short:
        preflight = readsav('eis_calibration/preflight_calib_short.sav')
    if long:
        preflight = readsav('eis_calibration/preflight_calib_long.sav')
    wave = preflight['wave']
    ea = preflight['ea']
    return wave, ea

def is_eis_wavelength(input_wave):
    # Define the minimum and maximum wavelengths for the short and long wavelength ranges
    wave_sw_min = 165
    wave_sw_max = 213
    wave_lw_min = 245
    wave_lw_max = 292

    # Initialize variables to store whether the input wavelength belongs to the long or short range
    long = False
    short = False

    # Check if the input wavelength falls within the short wavelength range
    ps = (input_wave - wave_sw_min) * (wave_sw_max - input_wave)
    if ps > 0:
        short = True

    # Check if the input wavelength falls within the long wavelength range
    pl = (input_wave - wave_lw_min) * (wave_lw_max - input_wave)
    if pl > 0:
        long = True

    # Determine if the input wavelength belongs to either the short or long wavelength range
    out = long or short

    # Return whether the input wavelength belongs to the short or long wavelength range
    return short, long


def calib_2014(map):
    import sunpy.map
    import re
    
    match = re.search(r'\d+\.\d+', map.meta['line_id'])
    wvl_value = float(match.group())
    calib_ratio = eis_ea(wvl_value)/eis_ea_nrl(map.date.value, wvl_value)
    new_map = sunpy.map.Map(map.data*calib_ratio, map.meta)
    return new_map