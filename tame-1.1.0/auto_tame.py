#!/usr/bin/python

import numpy as np
from astropy.io import fits
import os
import csv
import pandas as pd
import pidly
import glob


if __name__ == "__main__":

    spectra = glob.glob("*wavsoln.fits")
    lowercut_space = np.linspace(0.95, 0.995, 10)

    for spectrum in spectra:
        spec_label = spectrum.split('_wavsoln')[0]
        print(spec_label)
        for lowercut in lowercut_space:

            # Read in Parameter File
            df = pd.read_csv('tame.par', delim_whitespace=True, header=None)

            # Modify Parameter File (Lowercut)
            df.at[df.index[df[0] == "LOWERCUT"].tolist()[0], 1] = lowercut
            df.at[df.index[df[0] == "WORKNAME"].tolist()[0], 1] = spec_label
            df.at[df.index[df[0] == "SPECTRUM"].tolist()[0], 1] = spec_label+'.lpx'
            df.at[df.index[df[0] == "LINELIST"].tolist()[0], 1] = spec_label+'.lines'
            df.at[df.index[df[0] == "OUTPUT"].tolist()[0], 1] = spec_label+'_auto.aout'

            # Write new Parameter File
            df.to_csv("tame.par", header=None, index=False, sep="\t")

            # Run TAME
            idl = pidly.IDL('/Applications/exelis/idl/bin/idl')
            idl('tame_silent')

        # Read Output File


