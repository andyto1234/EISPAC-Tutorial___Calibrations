# EIS Calibration Tutorial using EISPAC in Python

This repository provides a tutorial on calibrating Hinode EUV Imaging Spectrometer (EIS) data using the EISPAC package in Python. The tutorial covers three calibration methods:

1. Warren et al. 2014 calibration
2. Del Zanna et al. 2025 calibration
3. Young & Mondal 2026 calibration (suggested to use from 2022 April 1)

## Tutorial Contents

The tutorial covers the following topics:

1. Reading and fitting EIS data using EISPAC
2. Applying the recommended cube-level calibration workflow before fitting
3. Using the Warren et al. 2014, Del Zanna et al. 2025, and Young & Mondal 2026 calibration functions
4. Comparing the calibrated intensity maps with the default EISPAC preflight calibration
5. Comparing the calibration results between IDL and Python implementations

By the end of this tutorial, you will be able to calibrate EIS data using different methods and compare the results between Python and IDL implementations.

## Code Sample

The recommended workflow is to calibrate the `EISCube` before fitting, so the fit sees the wavelength-dependent calibration across the full spectral window:

```python
import eispac
from eis_calibration.eis_cube_calib import calibrate_cube

# Example code
data_filepath = ...
template = ...

preflight_cube = eispac.read_cube(data_filepath, template.central_wave, apply_radcal=False)

cube_2014 = calibrate_cube(counts_cube, "2014")
cube_2023 = calibrate_cube(counts_cube, "2023")
cube_2026 = calibrate_cube(counts_cube, "2026")

fit_res_2026 = eispac.fit_spectra(cube_2026, template)
```

The older map-level helpers are still available as convenient post-fit shortcuts, but they are approximations because they correct only the final intensity map:

```python
import eispac
from eis_calibration.eis_calib_2014 import calib_2014
from eis_calibration.eis_calib_2023 import calib_2023
from eis_calibration.eis_calib_2026 import calib_2026

preflight_cube = eispac.read_cube(data_filepath, template.central_wave, apply_radcal=True)
fit_res_preflight = eispac.fit_spectra(preflight_cube, template)
int_map = fit_res_preflight.get_map(0, "int")

calibrated_map_2014 = calib_2014(int_map)
calibrated_map_2023 = calib_2023(int_map)
calibrated_map_2026 = calib_2026(int_map)
```

The Young & Mondal 2026 calibration uses effective area curves derived for a single date, `2024-09-30`. The cube-level and map-level APIs both emit a warning whenever this calibration is used, and they add date-range warnings for observations before `2022-04-01` or after `2024-09-30`.

## Citation

If you use these calibration routines, please cite the relevant calibration paper(s):

- Warren et al. 2014 for the Warren calibration
- Del Zanna et al. 2025 for the updated in-flight radiometric calibration
- Young & Mondal 2026 for the 2024 September 30 effective area curves

It would really help my work to cite this repository. For example, just a footnote:

> The EIS calibration routines used here were reproduced in Python by Andy S.H. To and are available at https://github.com/andyto1234/EISPAC-Tutorial___Calibrations. This repository provides Python implementations that reproduce the SolarSoftWare (SSW) IDL calibration workflow.

```bibtex
@ARTICLE{Warren2014ApJS..213...11W,
       author = {{Warren}, Harry P. and {Ugarte-Urra}, Ignacio and {Landi}, Enrico},
        title = "{The Absolute Calibration of the EUV Imaging Spectrometer on Hinode}",
      journal = {\apjs},
     keywords = {Sun: corona, Astrophysics - Solar and Stellar Astrophysics},
         year = 2014,
        month = jul,
       volume = {213},
       number = {1},
          eid = {11},
        pages = {11},
          doi = {10.1088/0067-0049/213/1/11},
archivePrefix = {arXiv},
       eprint = {1310.5324},
 primaryClass = {astro-ph.SR},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2014ApJS..213...11W},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{DelZanna2025ApJS..276...42D,
       author = {{Del Zanna}, G. and {Weberg}, M.~J. and {Warren}, H.~P.},
        title = "{Hinode EIS: Updated In-flight Radiometric Calibration}",
      journal = {\apjs},
     keywords = {The Sun, Solar extreme ultraviolet emission, Calibration, 1693, 1493, 2179, Astrophysics - Solar and Stellar Astrophysics},
         year = 2025,
        month = feb,
       volume = {276},
       number = {2},
          eid = {42},
        pages = {42},
          doi = {10.3847/1538-4365/ad981f},
archivePrefix = {arXiv},
       eprint = {2308.06609},
 primaryClass = {astro-ph.SR},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2025ApJS..276...42D},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{Young2026arXiv260504223Y,
       author = {{Young}, Peter R. and {Mondal}, Biswajit},
        title = "{Modeling Flare Continuum Emission Observed by Hinode/EIS: Instrument Calibration and Element Composition Results}",
      journal = {arXiv e-prints},
     keywords = {Solar and Stellar Astrophysics},
         year = 2026,
        month = may,
          eid = {arXiv:2605.04223},
        pages = {arXiv:2605.04223},
          doi = {10.48550/arXiv.2605.04223},
archivePrefix = {arXiv},
       eprint = {2605.04223},
 primaryClass = {astro-ph.SR},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2026arXiv260504223Y},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```
