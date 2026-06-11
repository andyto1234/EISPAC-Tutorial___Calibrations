import datetime
import re
from functools import lru_cache
from importlib import resources
import warnings

import numpy as np

from eis_calibration.eis_calib_2014 import eis_ea


CALIBRATION_DATE = datetime.date(2024, 9, 30)
RECOMMENDED_START_DATE = datetime.date(2022, 4, 1)

SW_RANGE = (165.0, 213.0)
LW_RANGE = (245.0, 292.0)

SW_FILE = "eis_eff_area_cont_20240930_sw.txt"
LW_FILE = "eis_eff_area_cont_20240930_lw.txt"


def _data_path(filename):
    return resources.files("eis_calibration").joinpath(
        "data", "young_mondal_2024", filename
    )


@lru_cache(maxsize=None)
def _read_effective_area(channel):
    if channel == "SW":
        filename = SW_FILE
    elif channel == "LW":
        filename = LW_FILE
    else:
        raise ValueError("ERROR: channel must be 'SW' or 'LW'")

    data = np.loadtxt(_data_path(filename), comments="#")
    return data[:, 0], data[:, 1]


def _validate_wavelengths(wavelength):
    wave = np.atleast_1d(np.asarray(wavelength, dtype=float))
    in_sw = (wave >= SW_RANGE[0]) & (wave <= SW_RANGE[1])
    in_lw = (wave >= LW_RANGE[0]) & (wave <= LW_RANGE[1])

    if not np.all(in_sw | in_lw) or (np.any(in_sw) and np.any(in_lw)):
        raise ValueError(
            "ERROR: Invalid wavelength(s). Please only select values in either "
            "the short (165 - 213) or long (245 - 292) wavelength bands."
        )

    return wave, "SW" if np.all(in_sw) else "LW"


def _interp_effective_area(wavelength, ref_wave, ref_ea):
    out_ea = np.zeros_like(wavelength, dtype=float)

    for idx, wave in enumerate(wavelength):
        exact = np.isclose(ref_wave, wave, rtol=0.0, atol=1e-10)
        if np.any(exact) and ref_ea[exact][0] <= 0.0:
            out_ea[idx] = 0.0
            continue

        loc = np.searchsorted(ref_wave, wave) - 1
        loc = max(0, min(loc, len(ref_wave) - 2))
        ea_pair = ref_ea[loc : loc + 2]

        if np.all(ea_pair > 0.0):
            out_ea[idx] = np.exp(
                np.interp(wave, ref_wave[ref_ea > 0.0], np.log(ref_ea[ref_ea > 0.0]))
            )
        else:
            out_ea[idx] = np.interp(wave, ref_wave, ref_ea)

    return out_ea


def young_mondal_ea(wavelength, short=False, long=False):
    if short and long:
        raise ValueError("ERROR: please select only one of short=True or long=True")

    if short:
        _, ea = _read_effective_area("SW")
        return ea

    if long:
        _, ea = _read_effective_area("LW")
        return ea

    scalar_input = np.isscalar(wavelength)
    wave, channel = _validate_wavelengths(wavelength)
    ref_wave, ref_ea = _read_effective_area(channel)

    out_ea = _interp_effective_area(wave, ref_wave, ref_ea)

    if scalar_input:
        return out_ea[0]
    return out_ea


def _parse_observation_date(date_value):
    if isinstance(date_value, bytes):
        date_value = date_value.decode("utf-8")

    date_text = str(date_value).strip()
    if date_text.endswith("Z"):
        date_text = date_text[:-1]

    try:
        return datetime.datetime.fromisoformat(date_text).date()
    except ValueError:
        return datetime.datetime.strptime(date_text[:10], "%Y-%m-%d").date()


def _warn_for_observation_date(date_value):
    obs_date = _parse_observation_date(date_value)
    warnings.warn(
        "WARNING: Young & Mondal 2026 effective area is for a single date "
        "(2024-09-30).",
        UserWarning,
        stacklevel=2,
    )

    if obs_date < RECOMMENDED_START_DATE:
        warnings.warn(
            "WARNING: Selected date is before 2022-04-01. Young & Mondal "
            "recommend these effective area curves for datasets obtained since "
            "2022 April.",
            UserWarning,
            stacklevel=2,
        )

    if obs_date > CALIBRATION_DATE:
        warnings.warn(
            "WARNING: Selected date is after the calibrated date on 2024-09-30. "
            "Returning the 2024-09-30 effective area.",
            UserWarning,
            stacklevel=2,
        )


def calib_2026(map, ratio=False):
    import sunpy.map

    warnings.warn(
        "calib_2026() applies a post-fit approximation to the intensity map. "
        "If the effective-area shape changes across the fitted spectral window, "
        "prefer calibrate_cube(...) before fit_spectra(...).",
        UserWarning,
        stacklevel=2,
    )
    match = re.search(r"\d+\.\d+", map.meta["line_id"])
    if match is None:
        raise ValueError("ERROR: Could not find a wavelength in map.meta['line_id']")

    wvl_value = float(match.group())
    _warn_for_observation_date(map.date.value)

    calib_ratio_2026 = eis_ea(wvl_value) / young_mondal_ea(wvl_value)
    new_map = sunpy.map.Map(map.data * calib_ratio_2026, map.meta)

    if ratio:
        return new_map, calib_ratio_2026
    return new_map
