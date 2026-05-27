# EIS Calibration Tutorial using EISPAC in Python

This repository provides a tutorial on calibrating Hinode EUV Imaging Spectrometer (EIS) data using the EISPAC package in Python. The tutorial covers three calibration methods:

1. Warren et al. 2014 calibration
2. Del Zanna et al. 2023 calibration
3. Young & Mondal 2024 calibration for the 2024 September 30 effective area curves

## Tutorial Contents

The tutorial covers the following topics:

1. Reading and fitting EIS data using EISPAC
2. Retrieving and applying the Warren et al. 2014, Del Zanna et al. 2023, and Young & Mondal 2024 calibration functions
3. Comparing the calibrated intensity maps with the default EISPAC preflight calibration
4. Comparing the calibration results between IDL and Python implementations

By the end of this tutorial, you will be able to calibrate EIS data using different methods and compare the results between Python and IDL implementations.

## Code Sample

I think the tutorial makes it look a bit more complex than it is. To apply calibration to an eispac map 'int_map', you just have to do:

```python
from eis_calibration.eis_calib_2023 import calib_2023
from eis_calibration.eis_calib_2024 import calib_2024

# Example code
int_map = ... # Load or create your eispac map

calibrated_map = calib_2023(int_map)
calibrated_map_2024 = calib_2024(int_map)
```

The Young & Mondal 2024 calibration uses effective area curves derived for a single date, 2024-09-30. The function prints a warning whenever it is used, and adds date-range warnings for observations before 2022-04-01 or after 2024-09-30.

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
