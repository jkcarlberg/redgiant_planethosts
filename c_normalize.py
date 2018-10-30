#!/usr/bin/python
import numpy as np


def c_normalize(spec, wave, window=None, hsig=6, npoly=3, median_replace=True, ignore=0, cheby=True, low_cut=0):
    """
    Continuum normalize a spectrum.

    The code runs through across the spectrum, looking at small windows at a time. In each window, it decides which
    points appear to be continuum and gives those pixels a weight of "1" and apparent non-continuum points a weight
    of "0". Since the window slides across the spectrum, each pixel will be in window many times (if window is 20
    pixels wide, each pixel will be in the box 20 times).  When a polynomial is fit to the continuum, they are weighted
    by the likeihood that they are true continuum points by the accumlated weight devised by the sliding window.

    Parameters
    ----------
    spec: array
        the spectrum to normalize
    wave: array
        wavelength array that corresponds to spec
    window: int, optional
        size of the window in pixels. Default is the greater of npix/20 or 10 pixels
    hsig: int, optional
        high sigma clip. Default is 6.
    npoly: int, optional
        order of polynomial to fit. Default is 3.
    median_replace: bool, optional
        flag to replace non-continuum points in the window with the median of the window. Default is True
    ignore: int, optional
        number of pixels on either side edge of the spectrum to ignore in the fit. Default is 0.
    cheby: bool, optional
        flag to fit spectrum using chebyshev polynomials (numpy.polynomial.chebyshev). Default is True
    low_cut: int, optional
        ignore pixel values below this value. Default is 0.

    Returns
    -------
    tuple: tuple containing:
        continuum_level (float): fitted continuum level
        norm_spec (array): normalized spectrum
        fit_pts (array): array of indices used in the fitting

    """
    pass

