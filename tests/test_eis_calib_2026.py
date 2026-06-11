import os
import sys
import tempfile
import types
import unittest
import warnings
from pathlib import Path
from unittest import mock

import numpy as np


TMP_SUNPY_CONFIG = tempfile.TemporaryDirectory()
Path(TMP_SUNPY_CONFIG.name).mkdir(parents=True, exist_ok=True)
os.environ.setdefault("SUNPY_CONFIGDIR", TMP_SUNPY_CONFIG.name)

from eis_calibration.eis_calib_2026 import calib_2026, young_mondal_ea


class FakeDate:
    def __init__(self, value):
        self.value = value


class FakeMapInput:
    def __init__(self, date_value):
        self.data = np.ones((2, 2))
        self.meta = {"line_id": "Fe XIII 203.826"}
        self.date = FakeDate(date_value)


class FakeSunpyMap:
    def __init__(self, data, meta):
        self.data = data
        self.meta = meta


def fake_sunpy_modules():
    sunpy_module = types.ModuleType("sunpy")
    sunpy_map_module = types.ModuleType("sunpy.map")
    sunpy_map_module.Map = FakeSunpyMap
    sunpy_module.map = sunpy_map_module
    return {"sunpy": sunpy_module, "sunpy.map": sunpy_map_module}


class TestEisCalib2026(unittest.TestCase):
    def test_effective_area_lookup_returns_positive_values(self):
        self.assertGreater(young_mondal_ea(203.0), 0.0)
        self.assertGreater(young_mondal_ea(262.0), 0.0)

    def test_out_of_band_wavelength_raises(self):
        with self.assertRaisesRegex(ValueError, "Invalid wavelength"):
            young_mondal_ea(230.0)

    def test_calibration_ratio_path_returns_map_and_scalar_ratio(self):
        with mock.patch.dict(sys.modules, fake_sunpy_modules()):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                new_map, ratio = calib_2026(
                    FakeMapInput("2024-09-30T23:59:00"),
                    ratio=True,
                )

        self.assertIsInstance(new_map, FakeSunpyMap)
        self.assertTrue(np.isfinite(ratio))
        self.assertGreater(ratio, 0.0)
        messages = [str(item.message) for item in caught]
        self.assertTrue(any("post-fit approximation" in message for message in messages))

    def test_warning_messages_are_emitted(self):
        cases = [
            ("2021-01-01T00:00:00", "before 2022-04-01"),
            ("2024-10-01T00:00:00", "after the calibrated date on 2024-09-30"),
        ]

        for date_value, expected_warning in cases:
            with self.subTest(date_value=date_value):
                with mock.patch.dict(sys.modules, fake_sunpy_modules()):
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        calib_2026(FakeMapInput(date_value))

                text = " ".join(str(item.message) for item in caught)
                self.assertIn("single date (2024-09-30)", text)
                self.assertIn(expected_warning, text)
                self.assertIn("post-fit approximation", text)


if __name__ == "__main__":
    unittest.main()
