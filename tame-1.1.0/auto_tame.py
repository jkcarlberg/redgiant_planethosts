#!/usr/bin/python

import numpy as np
from astropy.io import fits
import os
import csv
import pandas as pd
import pidly


if __name__ == "__main__":

    # Read in Parameter File
    df = pd.read_csv('tame.par', delim_whitespace=True, header=None)
    print(df.columns)

    # Modify Parameter File (Lowercut)
    df.at[df.index[df[0] == "LOWERCUT"].tolist()[0], 1] = 0.97

    # Write new Parameter File
    df.to_csv("tame.par", header=None, index=False, sep="\t")

    # Run TAME
    idl = pidly.IDL('/Applications/exelis/idl/bin/idl')
    idl('tame_silent')

    # Read Output File


