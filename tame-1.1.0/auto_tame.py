#!/usr/bin/python

import numpy as np
import pandas as pd
import pidly
import glob
import json


if __name__ == "__main__":

    input_dir = "../data/ew_known/tame_inputs/"
    output_dir = "../data/ew_known/tame_outputs_windowsize/"

    spectra = glob.glob(input_dir + "*wavsoln.fits")
    parameter = 'SPACING'
    parameter_space = np.linspace(1.5, 5.5, 5)
    idl = pidly.IDL('/Applications/exelis/idl/bin/idl')

    for spectrum in spectra:

        spec_label = spectrum.split('/')[-1].split('_wavsoln')[0]
        print(spec_label)
        line_dict = {}
        for parameter_value in parameter_space:

            # Read in Parameter File
            df = pd.read_csv('tame.par', delim_whitespace=True, header=None)

            # Modify Parameter File (Sweep Parameter & Working File)
            df.at[df.index[df[0] == "LOWERCUT"].tolist()[0], 1] = '0.99'  # Obtained from extended_calibration.ipynb
            df.at[df.index[df[0] == "WORKNAME"].tolist()[0], 1] = input_dir + spec_label
            df.at[df.index[df[0] == "SPECTRUM"].tolist()[0], 1] = input_dir + spec_label+'.lpx'
            #df.at[df.index[df[0] == "LINELIST"].tolist()[0], 1] = spec_label+'.lines'
            df.at[df.index[df[0] == "LINELIST"].tolist()[0], 1] = input_dir + 'input_lines.lines'
            df.at[df.index[df[0] == "OUTPUT"].tolist()[0], 1] = output_dir + spec_label + str(parameter_value) + '_auto.aout'
            df.at[df.index[df[0] == "SMOOTHER"].tolist()[0], 1] = "1"

            df.at[df.index[df[0] == parameter].tolist()[0], 1] = parameter_value

            # Write new Parameter File
            df.to_csv("tame.par", header=None, index=False, sep="\t")

            # Run TAME
            idl('tame_silent')

            # Read Output File
            tame_ew = pd.read_csv("{}{}{}_auto.aout".format(output_dir,spec_label, str(parameter_value)), skiprows=1,
                                  delim_whitespace=True, header=None)
            tame_df = tame_ew[[0, 4, 6]]  # Wavelength and Equivalent Width
            for line, ew, linecent in np.array(tame_df).tolist():
                if line not in line_dict:
                    line_dict[line] = [(parameter_value, ew, linecent)]
                else:
                    line_dict[line].append((parameter_value, ew, linecent))

        print(line_dict)
        with open('{}{}.json'.format(output_dir, spec_label), 'w') as fp:
            json.dump(line_dict, fp)


