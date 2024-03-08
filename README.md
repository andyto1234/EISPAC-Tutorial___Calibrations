# Creating a Fit Template for EISPAC

This repository provides a tutorial on creating a new fit template for EIS (Extreme-ultraviolet Imaging Spectrometer) data, focusing on the Fe XIII 203.83 line, which is a standard line for EIS density diagnostics.

The default template in EISPAC only fits 2 Gaussians. In this we fit 3 Guassian according to the EIS software notes.

This code expands on Alexandros Koukras's tutorial on creating single peak EISPAC template. https://github.com/andyto1234/EIS_data_analysis/blob/main/Making_an_EIS_fit_template.ipynb

## Table of Contents
1. [The Fit Template](#the-fit-template)
2. [Fitting the Data](#fitting-the-data)
3. [Creating a New Template](#creating-a-new-template)
4. [Fitting Spectra with the New Template](#fitting-spectra-with-the-new-template)
5. [Examining the Fit Result](#examining-the-fit-result)

## Requirements
- Python 3.x
- eispac
- astropy
- scipy
- numpy
- matplotlib
- h5py

## Special Thanks
We used Claude 3 LLM to create this README.md 