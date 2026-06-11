import contextlib
import copy
import io
import os
import tempfile
import unittest
import warnings
from pathlib import Path

import numpy as np
from astropy import units as u


TMP_SUNPY_CONFIG = tempfile.TemporaryDirectory()
Path(TMP_SUNPY_CONFIG.name).mkdir(parents=True, exist_ok=True)
os.environ.setdefault("SUNPY_CONFIGDIR", TMP_SUNPY_CONFIG.name)

from eis_calibration.eis_calib_2014 import eis_ea
from eis_calibration.eis_calib_2026 import young_mondal_ea
from eis_calibration.eis_cube_calib import calibrate_cube


class FakeUncertainty:
    def __init__(self, array):
        self.array = np.asarray(array, dtype=float)


class FakeCube:
    def __init__(self, data, meta, unit=u.photon, radcal=None, uncertainty=None):
        self.data = np.asarray(data, dtype=float)
        self.meta = copy.deepcopy(meta)
        self.unit = unit
        self.radcal = None if radcal is None else np.asarray(radcal, dtype=float)
        if uncertainty is None:
            uncertainty = np.ones_like(self.data)
        self.uncertainty = FakeUncertainty(uncertainty)

    def apply_radcal(self, input_radcal=None):
        if input_radcal is None:
            input_radcal = self.meta["radcal"]

        radcal = np.asarray(input_radcal, dtype=float)
        factor = radcal if self.radcal is None else radcal / self.radcal
        new_meta = copy.deepcopy(self.meta)
        new_meta["notes"] = list(new_meta.get("notes", []))
        new_meta["mod_index"] = dict(new_meta.get("mod_index", {}))
        new_meta["mod_index"]["bunit"] = "erg / (cm2 s sr)"
        return FakeCube(
            self.data * factor.reshape((1, 1, -1)),
            new_meta,
            unit=u.Unit("erg / (cm2 s sr)"),
            radcal=radcal,
            uncertainty=self.uncertainty.array * factor.reshape((1, 1, -1)),
        )

    def remove_radcal(self):
        if self.radcal is None:
            return self

        factor = self.radcal.reshape((1, 1, -1))
        new_meta = copy.deepcopy(self.meta)
        new_meta["notes"] = list(new_meta.get("notes", []))
        new_meta["mod_index"] = dict(new_meta.get("mod_index", {}))
        new_meta["mod_index"]["bunit"] = "photon"
        return FakeCube(
            self.data / factor,
            new_meta,
            unit=u.photon,
            radcal=None,
            uncertainty=self.uncertainty.array / factor,
        )


def make_fake_cube(wave, date_obs, preflight_radcal=None, counts=None):
    wave = np.asarray(wave, dtype=float)
    if preflight_radcal is None:
        preflight_radcal = np.ones_like(wave)
    if counts is None:
        counts = np.ones((2, 2, len(wave)), dtype=float)
    meta = {
        "wave": wave,
        "radcal": np.asarray(preflight_radcal, dtype=float),
        "date_obs": np.asarray(date_obs, dtype=object),
        "notes": [],
        "mod_index": {"bunit": "photon"},
    }
    return FakeCube(counts, meta, unit=u.photon, radcal=None)


class TestCubeCalibration(unittest.TestCase):
    def test_counts_cube_applies_requested_radcal_curve(self):
        wave = np.linspace(203.60, 204.10, 24)
        preflight_radcal = np.linspace(10.0, 12.0, len(wave))
        cube = make_fake_cube(wave, ["2024-09-30T00:00:00"], preflight_radcal)

        calibrated = calibrate_cube(cube, "2026", date="2024-09-30T00:00:00")
        expected = preflight_radcal * eis_ea(wave) / young_mondal_ea(wave)

        self.assertTrue(np.allclose(calibrated.radcal, expected))
        self.assertTrue(np.allclose(calibrated.data[0, 0], expected))
        self.assertEqual(calibrated.meta["calib_method"], "2026")
        self.assertEqual(calibrated.meta["calib_source"], "Young & Mondal 2026")
        self.assertEqual(calibrated.meta["calib_date_used"], "2024-09-30T00:00:00")
        self.assertEqual(calibrated.meta["calib_scope"], "cube")
        self.assertTrue(calibrated.meta["calib_preserves_meta_radcal"])
        self.assertTrue(np.allclose(calibrated.meta["radcal"], preflight_radcal))

    def test_preflight_cube_replaced_with_requested_calibration(self):
        wave = np.linspace(203.60, 204.10, 24)
        preflight_radcal = np.linspace(10.0, 12.0, len(wave))
        counts_cube = make_fake_cube(wave, ["2024-09-30T00:00:00"], preflight_radcal)
        preflight_cube = counts_cube.apply_radcal(preflight_radcal)

        calibrated = calibrate_cube(preflight_cube, "2026", date="2024-09-30T00:00:00")
        expected = preflight_radcal * eis_ea(wave) / young_mondal_ea(wave)

        self.assertTrue(np.allclose(calibrated.radcal, expected))
        self.assertTrue(np.allclose(calibrated.data[0, 0], expected))

    def test_custom_calibrated_cube_raises(self):
        wave = np.linspace(203.60, 204.10, 24)
        preflight_radcal = np.linspace(10.0, 12.0, len(wave))
        counts_cube = make_fake_cube(wave, ["2024-09-30T00:00:00"], preflight_radcal)
        custom_cube = counts_cube.apply_radcal(preflight_radcal * 1.05)

        with self.assertRaisesRegex(ValueError, "original pre-flight"):
            calibrate_cube(custom_cube, "2026", date="2024-09-30T00:00:00")

    def test_wavelength_radcal_length_mismatch_raises(self):
        wave = np.linspace(203.60, 204.10, 24)
        cube = make_fake_cube(wave, ["2024-09-30T00:00:00"])
        cube.meta["radcal"] = np.ones(len(wave) - 1)

        with self.assertRaisesRegex(ValueError, "same length"):
            calibrate_cube(cube, "2026", date="2024-09-30T00:00:00")

    def test_2026_automatic_date_warning_is_emitted(self):
        wave = np.linspace(203.60, 204.10, 24)
        cube = make_fake_cube(
            wave,
            ["2021-01-01T00:00:00", "2021-01-01T00:30:00"],
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            calibrate_cube(cube, "2026")

        messages = " ".join(str(item.message) for item in caught)
        self.assertIn("single date (2024-09-30)", messages)
        self.assertIn("before 2022-04-01", messages)

    def test_2023_automatic_date_warning_is_preserved(self):
        wave = np.linspace(203.60, 204.10, 24)
        cube = make_fake_cube(
            wave,
            ["2024-09-30T00:00:00", "2024-09-30T00:30:00"],
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            calibrated = calibrate_cube(cube, "2023")

        self.assertTrue(np.all(np.isfinite(calibrated.radcal)))
        self.assertIn("after the last calibrated date", output.getvalue())

    def test_narrow_window_postfit_approximation_stays_close(self):
        wave0 = 203.59861160594346
        dw = 0.022274225288896332
        wave = wave0 + np.arange(24) * dw
        line_center = 203.826
        sigma = 0.035
        counts_profile = np.exp(-0.5 * ((wave - line_center) / sigma) ** 2)
        counts = counts_profile.reshape((1, 1, -1))
        cube = make_fake_cube(
            wave,
            ["2024-09-30T00:00:00"],
            preflight_radcal=np.ones_like(wave),
            counts=counts,
        )

        proper_cube = calibrate_cube(cube, "2026", date="2024-09-30T00:00:00")
        proper_intensity = proper_cube.data.sum(axis=-1)

        approx_ratio = eis_ea(line_center) / young_mondal_ea(line_center)
        approx_intensity = counts.sum(axis=-1) * approx_ratio
        rel_diff = np.abs(proper_intensity - approx_intensity) / proper_intensity

        self.assertLess(float(rel_diff.max()), 0.02)


if __name__ == "__main__":
    unittest.main()
