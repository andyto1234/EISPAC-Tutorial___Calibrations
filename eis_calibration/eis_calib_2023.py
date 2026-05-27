import datetime
import re
import numpy as np
from scipy.interpolate import interp1d
from scipy.io import readsav
from eis_calibration.eis_calib_2014 import eis_ea
import sunpy.map

def anytim2tai(time_str):
    """
    Converts a given time string into TAI (Temps Atomique International) format.

    Parameters
    ----------
    time_str : str
        The time string to be converted. It should be in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns
    -------
    float
        The corresponding TAI time value as seconds since 1 January 1958.

    Notes
    -----
    This function assumes that the input time string is in UTC (Coordinated Universal Time).
    The conversion from UTC to TAI is based on the assumption that TAI is always ahead of UTC
    by a fixed offset of 37 seconds.

    """
    time_str = re.sub(r'[^\w\s.]', '', time_str)
    # Split the input time string into the main part and the fractional part (if present)
    time_str, _, fractional_part = time_str.partition('.')

    # Check if the time string contains a 'T' separator
    if 'T' in time_str:
        # Split the date and time components using the 'T' separator
        date_str, time_str = time_str.split('T')
        # Combine the date and time components with a space separator
        time_str = f"{date_str} {time_str}"
    else:
        # Remove any non-alphanumeric characters from the time string
        time_str = re.sub(r'[^\w\s]', '', time_str)

    # Parse the input time string into a datetime object
    dt = datetime.datetime.strptime(time_str, '%Y%m%d %H%M%S')

    # Calculate the number of seconds since the Unix epoch (1 January 1970)
    seconds_since_epoch = (dt - datetime.datetime(1970, 1, 1)).total_seconds()

    # Calculate the number of seconds between the TAI epoch (1 January 1958) and the Unix epoch
    tai_offset = (datetime.datetime(1970, 1, 1) - datetime.datetime(1958, 1, 1)).total_seconds()

    # Add the offset to the seconds since the Unix epoch to get the TAI time value
    tai_time = seconds_since_epoch + tai_offset

    # Add the fixed offset between UTC and TAI (37 seconds)
    tai_time += 37

    return tai_time

from scipy.interpolate import InterpolatedUnivariateSpline

def interpol_eis_ea(date, wavelength, short=False, long=False, radcal=False, ea_file=None, quiet=False):
    # Validate input values
    if np.size(date) != 1:
        raise ValueError('ERROR: please input a single date')
    
    in_tai = anytim2tai(date)

    if in_tai < anytim2tai('2006-10-20T10:20:00.000'):
        print('WARNING: Selected date is before the start of normal EIS science operations. Output values may be inaccurate.')

    if not short and not long:
        n_input_wave = np.size(wavelength)
        loc_short = np.where((wavelength >= 165) & (wavelength <= 213))[0]
        loc_long = np.where((wavelength >= 245) & (wavelength <= 292))[0]
        if (len(loc_short) + len(loc_long) < n_input_wave) or (len(loc_short) > 0 and len(loc_long) > 0):
            raise ValueError('ERROR: Invalid wavelength(s). Please only select values in either the short (165 - 213) or long (245 - 292) wavelength bands.')

    if short:
        wavelength = 1
    elif long:
        wavelength = 1000

    fit_ea = readsav('eis_calibration/fit_eis_ea_2023-05-04.sav')['fit_ea']
    # Extract the necessary data from the loaded file
    fit_dates = fit_ea.date_obs[0].astype(str)
    fit_easw = fit_ea.sw_ea[0]
    fit_ealw = fit_ea.lw_ea[0]
    sw_wave = fit_ea.sw_wave[0]
    lw_wave = fit_ea.lw_wave[0]

    ref_tai = np.array([anytim2tai(date) for date in fit_dates])

    if in_tai < ref_tai[0]:
        if not quiet:
            print(f"WARNING: Selected date is before the first calibrated date on {fit_ea.date_obs[0]}. Returning first fit calibration")
        in_tai = ref_tai[0]

    if in_tai > ref_tai[-1]:
        if not quiet:
            print(f"WARNING: Selected date is after the last calibrated date on {fit_ea.date_obs[-1][-1]}. Returning last fit calibration")
        in_tai = ref_tai[-1]

    # Select out the desired waveband
    if short or (np.size(wavelength) > 0 and np.max(wavelength) < 220):
        ref_ea = fit_easw
        ref_wave = sw_wave
    else:
        ref_ea = fit_ealw
        ref_wave = lw_wave

    # Interpolate the EA curve to the selected date and wavelength value
    n_ref_waves = len(ref_wave)
    new_ea = np.zeros(n_ref_waves)
    for w in range(n_ref_waves):
        ea_values = ref_ea[w,:]
        new_ea[w] = np.interp(in_tai, ref_tai, ea_values)
        
    if not short and not long:
        out_ea = interp1d(ref_wave, new_ea, kind='cubic')(wavelength)
    else:
        wavelength = ref_wave
        out_ea = new_ea

    # Compute the radcal curve or value (if requested)
    if radcal:
        # Define unit conversion factors
        sr_factor = (725.0 / 1.496e8) ** 2
        ergs_to_photons = 6.626e-27 * 2.998e10 * 1.e8
        gain = 6.3
        phot_to_elec = 12398.5 / 3.65
        tau_sensitivity = 1894.0

        print('Returning radcal values for converting [DN/s] to [ergs/(sr cm^2 s)]')
        print('   Note: You may still need to adjust for exposure time and slitsize.')

        # Convert from [DN/s] to [photons/(arcsec^2 * cm^2 * s)]
        radcal = (wavelength * gain) / (out_ea * phot_to_elec)

        # Convert to units of [ergs/(sr cm^2 s)]
        radcal = radcal * ergs_to_photons / wavelength / sr_factor

        out_ea = radcal

    return out_ea

def calib_2023(map, ratio = False):
    match = re.search(r'\d+\.\d+', map.meta['line_id'])
    wvl_value = float(match.group())
    calib_ratio_2023 = eis_ea(wvl_value)/interpol_eis_ea(map.date.value, wvl_value)
    new_map = sunpy.map.Map(map.data*calib_ratio_2023, map.meta)
    if ratio:
        return new_map, calib_ratio_2023
    else:
        return new_map