# Creating a Fit Template for EISPAC and Calculating Fe XIII Density

This repository provides two tutorials:

1. [Creating a new fit template](https://github.com/andyto1234/EISPAC-Tutorial___Fe-XIII-Density/blob/main/Tutorial__Making_an_EIS_fit_template.ipynb) for EIS (Extreme-ultraviolet Imaging Spectrometer) data, focusing on the Fe XIII spectral lines.
2. [Calculating the density](https://github.com/andyto1234/EISPAC-Tutorial___Fe-XIII-Density/blob/main/Tutorial__Calculate_FeXIII_Density.ipynb) of Fe XIII using the EISPAC package in Python.

## Fit Template Tutorial

The default template in EISPAC only fits 2 Gaussians. In this tutorial, we fit 3 Gaussians according to the EIS software notes.

This code expands on [Alexandros Koukras's tutorial](https://github.com/AlexandrosKoukras/EIS_data_analysis/blob/main/Making_an_EIS_fit_template.ipynb) on creating single peak EISPAC template.

## Fe XIII Density Calculation Tutorial

The Fe XIII density calculation tutorial demonstrates how to use the EISPAC package to calculate the density of Fe XIII from EIS data. It covers the following steps:

1. Reading in EIS data and Fe XIII templates
2. Fitting the spectra using the templates
3. Calculating the intensity ratio of the 203.83 Å and 202.04 Å lines
4. Converting the intensity ratio to density values using a pre-calculated density ratio table
5. Creating and plotting a density map using SunPy

This tutorial provides a practical example of how to use EISPAC for scientific analysis of EIS data, specifically for density diagnostics using the Fe XIII spectral lines.

## Requirements

\- Python 3.x
\- eispac
\- astropy
\- scipy
\- numpy
\- matplotlib
\- h5py

## Special Thanks

We used Claude 3 LLM to create this README.md.
