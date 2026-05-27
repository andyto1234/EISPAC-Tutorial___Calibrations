import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("SUNPY_CONFIGDIR", tempfile.mkdtemp(prefix="sunpy-config-"))
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mpl-config-"))

from eis_calibration.eis_calib_2014 import eis_ea
from eis_calibration.eis_calib_2023 import interpol_eis_ea
from eis_calibration.eis_calib_2026 import young_mondal_ea


def compare_calibrations(date, threshold):
    waves = np.r_[np.arange(165.0, 214.0, 1.0), np.arange(245.0, 293.0, 1.0)]

    ea_2023 = np.array(
        [interpol_eis_ea(date, wave, quiet=True) for wave in waves],
        dtype=float,
    )
    ea_2026 = np.array([young_mondal_ea(wave) for wave in waves], dtype=float)
    preflight = np.array([eis_ea(wave) for wave in waves], dtype=float)

    positive = (ea_2023 > 0.0) & (ea_2026 > 0.0) & (preflight > 0.0)
    ea_pct_diff = np.full_like(waves, np.nan, dtype=float)
    ea_pct_diff[positive] = 100.0 * (ea_2026[positive] - ea_2023[positive]) / ea_2023[positive]

    multiplier_2023 = np.full_like(waves, np.nan, dtype=float)
    multiplier_2026 = np.full_like(waves, np.nan, dtype=float)
    multiplier_2023[positive] = preflight[positive] / ea_2023[positive]
    multiplier_2026[positive] = preflight[positive] / ea_2026[positive]

    multiplier_pct_diff = np.full_like(waves, np.nan, dtype=float)
    multiplier_pct_diff[positive] = (
        100.0
        * (multiplier_2026[positive] - multiplier_2023[positive])
        / multiplier_2023[positive]
    )

    abs_multiplier_pct_diff = np.abs(multiplier_pct_diff)
    failing = positive & (abs_multiplier_pct_diff > threshold)

    print(f"Comparison date for 2023 calibration: {date}")
    print("The 2023 calibration clamps post-2022 dates to its last available curve.")
    print(f"Tolerance on applied calibration multiplier: {threshold:.1f}%")
    print(f"Wavelengths checked: {len(waves)}")
    print(f"Valid positive calibration wavelengths: {positive.sum()}")
    print(f"Excluded zero/nonpositive wavelengths: {(~positive).sum()}")
    print(f"Median absolute multiplier difference: {np.nanmedian(abs_multiplier_pct_diff):.2f}%")
    print(f"Mean absolute multiplier difference: {np.nanmean(abs_multiplier_pct_diff):.2f}%")
    print(f"Max absolute multiplier difference: {np.nanmax(abs_multiplier_pct_diff):.2f}%")
    print(f"Within tolerance: {(positive & ~failing).sum()} / {positive.sum()}")

    for lo, hi, name in [(165.0, 213.0, "SW"), (245.0, 292.0, "LW")]:
        band = positive & (waves >= lo) & (waves <= hi)
        band_fail = failing & (waves >= lo) & (waves <= hi)
        print("")
        print(f"{name} band")
        print(f"  Median absolute multiplier difference: {np.nanmedian(abs_multiplier_pct_diff[band]):.2f}%")
        print(f"  Max absolute multiplier difference: {np.nanmax(abs_multiplier_pct_diff[band]):.2f}%")
        print(f"  Within tolerance: {(band & ~band_fail).sum()} / {band.sum()}")

    print("")
    print("Wavelengths outside tolerance")
    if not np.any(failing):
        print("  None")
    else:
        print("  wave[A]  EA2023      EA2026      EA diff[%]  multiplier diff[%]")
        for idx in np.where(failing)[0]:
            print(
                f"  {waves[idx]:6.1f}  "
                f"{ea_2023[idx]:.7g}  "
                f"{ea_2026[idx]:.7g}  "
                f"{ea_pct_diff[idx]:+10.1f}  "
                f"{multiplier_pct_diff[idx]:+18.1f}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Compare EIS 2023 and Young & Mondal 2026 calibrations."
    )
    parser.add_argument(
        "--date",
        default="2024-09-30T00:00:00.000",
        help="Date passed to the 2023 calibration.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=30.0,
        help="Allowed absolute percent difference in applied calibration multiplier.",
    )
    args = parser.parse_args()

    compare_calibrations(args.date, args.threshold)


if __name__ == "__main__":
    main()
