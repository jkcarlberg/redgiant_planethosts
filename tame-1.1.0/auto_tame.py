#!/usr/bin/python

import numpy as np
import pandas as pd
import pidly
import glob
import json


if __name__ == "__main__":

    spectra = glob.glob("ngc2204*wavsoln.fits")
    lowercut_space = np.linspace(0.95, 0.995, 10)
    idl = pidly.IDL('/Applications/exelis/idl/bin/idl')

    for spectrum in spectra:

        spec_label = spectrum.split('_wavsoln')[0]
        print(spec_label)
        line_dict = {}
        for lowercut in lowercut_space:

            # Read in Parameter File
            df = pd.read_csv('tame.par', delim_whitespace=True, header=None)

            # Modify Parameter File (Lowercut & Working File)
            df.at[df.index[df[0] == "LOWERCUT"].tolist()[0], 1] = lowercut
            df.at[df.index[df[0] == "WORKNAME"].tolist()[0], 1] = spec_label
            df.at[df.index[df[0] == "SPECTRUM"].tolist()[0], 1] = spec_label+'.lpx'
            df.at[df.index[df[0] == "LINELIST"].tolist()[0], 1] = spec_label+'.lines'
            df.at[df.index[df[0] == "OUTPUT"].tolist()[0], 1] = spec_label+'_auto.aout'

            # Write new Parameter File
            df.to_csv("tame.par", header=None, index=False, sep="\t")

            # Run TAME
            idl('tame_silent')

            # Read Output File
            tame_ew = pd.read_csv("{}_auto.aout".format(spec_label), skiprows=1,
                                  delim_whitespace=True, header=None)
            tame_df = tame_ew[[0, 4]]  # Wavelength and Equivalent Width
            for line, ew in np.array(tame_df).tolist():
                if line not in line_dict:
                    line_dict[line] = [(lowercut, ew)]
                else:
                    line_dict[line].append((lowercut, ew))


        print(line_dict)
        with open('{}.json'.format(spec_label), 'w') as fp:
            json.dump(line_dict, fp)


