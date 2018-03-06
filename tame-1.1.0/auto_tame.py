#!/usr/bin/python

import numpy as np
from astropy.io import fits
import os
import csv
import pandas as pd
import pidly


if __name__ == "__main__":

    lowercut_space = np.linspace(0.95, 0.995, 10)
    for lowercut in lowercut_space:

        # Read in Parameter File
        df = pd.read_csv('tame.par', delim_whitespace=True, header=None)
        print(df.columns)

        # Modify Parameter File (Lowercut)
        df.at[df.index[df[0] == "LOWERCUT"].tolist()[0], 1] = lowercut

        # Write new Parameter File
        df.to_csv("tame.par", header=None, index=False, sep="\t")

        # Run TAME
        idl = pidly.IDL('/Applications/exelis/idl/bin/idl')
        idl('tame_silent')

    # Read Output File


