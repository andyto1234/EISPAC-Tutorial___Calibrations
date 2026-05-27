from setuptools import setup, find_packages

setup(
    name='eis_calibration',
    version='0.1.0',
    description='EIS Calibration Package',
    author='Andy S.H. To',
    author_email='andysh.to@esa.int',
    url='https://github.com/andyto1234/EISPAC-Tutorial___Calibrations/tree/main/eis_calibration',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'sunpy',
    ],
    package_data={
        'eis_calibration': ['fit_eis_ea_2023-05-04.sav',
                            'eis_calib_warren_2014.sav',
                            'preflight_calib_long.sav',
                            'preflight_calib_short.sav',
                            ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.9',

)