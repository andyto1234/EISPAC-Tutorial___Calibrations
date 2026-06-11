import datetime
from typing import Iterable

import numpy as np
from astropy import units as u

from eis_calibration.eis_calib_2014 import eis_ea, eis_ea_nrl
from eis_calibration.eis_calib_2023 import interpol_eis_ea
from eis_calibration.eis_calib_2026 import _warn_for_observation_date, young_mondal_ea


VALID_CALIBRATIONS = {"2014", "2023", "2026"}

CALIBRATION_SOURCES = {
    "2014": "Warren et al. 2014",
    "2023": "Del Zanna et al. 2025",
    "2026": "Young & Mondal 2026",
}


def _parse_datetime(value):
    if isinstance(value, datetime.datetime):
        return value

    if isinstance(value, bytes):
        value = value.decode("utf-8")

    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1]

    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        return datetime.datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S")


def _midpoint_date(date_values: Iterable):
    flattened = np.asarray(date_values, dtype=object).ravel()
    timestamps = []

    for value in flattened:
        if value in (None, ""):
            continue
        try:
            timestamps.append(_parse_datetime(value))
        except ValueError:
            continue

    if not timestamps:
        raise ValueError(
            "ERROR: Could not determine an observation date from cube.meta['date_obs']."
        )

    timestamps.sort()
    start = timestamps[0]
    end = timestamps[-1]
    midpoint = start + (end - start) / 2
    return midpoint.isoformat(timespec="seconds")


def _validate_calibration_name(calibration):
    calibration_name = str(calibration)
    if calibration_name not in VALID_CALIBRATIONS:
        options = ", ".join(sorted(VALID_CALIBRATIONS))
        raise ValueError(
            f"ERROR: calibration must be one of {options}. Got {calibration!r}."
        )
    return calibration_name


def _validate_wave_and_preflight(cube):
    wave = np.asarray(cube.meta["wave"], dtype=float)
    preflight_radcal = np.asarray(cube.meta["radcal"], dtype=float)

    if wave.ndim != 1 or preflight_radcal.ndim != 1:
        raise ValueError(
            "ERROR: cube.meta['wave'] and cube.meta['radcal'] must each be 1D arrays."
        )

    if len(wave) != len(preflight_radcal):
        raise ValueError(
            "ERROR: cube.meta['wave'] and cube.meta['radcal'] must have the same length."
        )

    return wave, preflight_radcal


def _is_counts_cube(cube):
    return cube.radcal is None and cube.unit == u.photon


def _is_preflight_cube(cube, preflight_radcal):
    return cube.radcal is not None and np.allclose(
        np.asarray(cube.radcal, dtype=float),
        preflight_radcal,
        rtol=1e-6,
        atol=1e-12,
    )


def _target_effective_area(calibration, obs_date, wave, quiet=False):
    if calibration == "2014":
        return np.asarray(eis_ea_nrl(obs_date, wave), dtype=float)

    if calibration == "2023":
        return np.asarray(interpol_eis_ea(obs_date, wave, quiet=quiet), dtype=float)

    _warn_for_observation_date(obs_date)
    return np.asarray(young_mondal_ea(wave), dtype=float)


def calibrate_cube(cube, calibration, date=None, quiet=False):
    """Apply an EIS radiometric calibration to an ``EISCube`` before fitting.

    Parameters
    ----------
    cube : EISCube-like
        A counts cube from ``eispac.read_cube(..., apply_radcal=False)`` or a
        cube with the original pre-flight calibration still applied.
    calibration : {"2014", "2023", "2026"}
        Target calibration to apply.
    date : str or datetime-like, optional
        Observation time used for time-dependent calibrations. If omitted, the
        midpoint of ``cube.meta["date_obs"]`` is used.
    quiet : bool, optional
        Passed through to the 2023 calibration lookup.
    """
    calibration_name = _validate_calibration_name(calibration)
    wave, preflight_radcal = _validate_wave_and_preflight(cube)

    if date is None:
        obs_date = _midpoint_date(cube.meta["date_obs"])
    else:
        obs_date = _parse_datetime(date).isoformat(timespec="seconds")

    if _is_counts_cube(cube):
        counts_cube = cube
    elif _is_preflight_cube(cube, preflight_radcal):
        counts_cube = cube.remove_radcal()
    else:
        raise ValueError(
            "ERROR: calibrate_cube(...) only accepts an uncalibrated counts cube "
            "or a cube with the original pre-flight calibration still applied."
        )

    preflight_ea = np.asarray(eis_ea(wave), dtype=float)
    target_ea = _target_effective_area(calibration_name, obs_date, wave, quiet=quiet)

    if np.any(target_ea <= 0.0):
        raise ValueError(
            "ERROR: The selected calibration returned a non-positive effective area "
            "inside the spectral window."
        )

    new_radcal = preflight_radcal * preflight_ea / target_ea
    calibrated_cube = counts_cube.apply_radcal(new_radcal)
    calibrated_cube.meta["calib_method"] = calibration_name
    calibrated_cube.meta["calib_source"] = CALIBRATION_SOURCES[calibration_name]
    calibrated_cube.meta["calib_date_used"] = obs_date
    calibrated_cube.meta["calib_scope"] = "cube"
    calibrated_cube.meta["calib_preserves_meta_radcal"] = True
    calibrated_cube.meta["notes"].append(
        f"Applied {calibration_name} EIS calibration with calibrate_cube()"
    )

    return calibrated_cube
