#!/usr/bin/python
import numpy as np
#from multiprocessing import Pool, cpu_count



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
    spec: numpy.array
        the spectrum to normalize
    wave: numpy.array
        wavelength array that corresponds to spec
    window: int, optional
        size of the sweeping window in pixels. Default is the greater of npix/20 or 10 pixels
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
    nspec = len(spec)

    spec_weight = np.zeros(nspec)
    new_spec = np.zeros(nspec)

    spec_median = np.median(spec)
    spec_sigma = np.std(spec)

    if window is None:
        winsize = max(nspec/20, 10)
    else:
        winsize = window

    all_sigma = np.zeros(nspec)
    # Loop through spectrum points
    for i in range(nspec):
        lowi = int(max(i - winsize/2, 0))
        highi = int(min(i + winsize/2, nspec))
        spec_chunk = spec[lowi:highi]
        sig_chunk = np.std(spec_chunk)
        all_sigma[i] = sig_chunk
    small_sigma = np.median(all_sigma)

    # Loop through spectrum points again
    for i in range(nspec):
        lowi = int(max(i - winsize / 2, 0))
        highi = int(min(i + winsize / 2, nspec))
        spec_chunk = spec[lowi:highi]
        mediani = np.median(spec_chunk)

        # find the maximum of all points that are within some sigma of the median
        maxpt = np.where(spec_chunk == max(spec_chunk[spec_chunk < mediani+hsig*small_sigma]))[0][0]
        print(maxpt)
        if median_replace:
            new_spec[i] = mediani
        else:
            spec_weight[maxpt+lowi] += 1

    specrange = np.arange(nspec, dtype='float')
    if median_replace:
        spec_mask = (np.array([specrange > winsize]) * np.array([specrange < (nspec-winsize)]))
    else:
        spec_mask = np.array([spec_weight != 0]) * np.array([specrange > winsize]) * np.array([
            specrange < nspec - winsize])
    ct_fit = np.sum(spec_mask)
    to_fit = np.where(spec_mask)[1]



if __name__ == "__main__":
    from astropy.io import fits
    from astropy.convolution import convolve, Box1DKernel
    s_hdu = fits.open("Data/ew_known/tame_inputs/col110_1134red_oned_25jan14_wavsoln.fits")

    s_data = s_hdu[1].data
    s_flux = s_data['FLUX']
    smoothed_flux = convolve(s_flux, Box1DKernel(5))
    s_flux = smoothed_flux
    s_wav = s_data['WAVEL']
    wav_mask = (s_wav > 5305) & (s_wav < 5310)
    s_flux = s_flux[wav_mask]
    s_wav = s_wav[wav_mask]
    c_normalize(s_flux, s_wav)



