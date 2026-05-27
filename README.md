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
