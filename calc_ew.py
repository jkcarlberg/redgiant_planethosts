#!/usr/bin/python

import numpy as np
import json
import pandas as pd
import glob


def calc_ew(file_list, linecorr):
    """Take the tame json output files and apply linecorr adjustments to extract calibrated equivalent widths"""

    # Read in the files
    files = glob.glob(file_list)
    corr_df = pd.read_csv(linecorr, delim_whitespace=True)

    #Iterate over file list
    for file in files:
        fname = file.split('/')[-1].split('.')[0]
        print(fname)
        out_file = fname+".ew"
        out_df = pd.DataFrame({"Line": [], "EW": [], "Uncertainty": []})
        out_df = out_df[["Line", "EW", "Uncertainty"]]

        #Read in json file
        with open(file) as json_file:
            lowcut_ew = json.load(json_file)

            #Iterate over lines
            for index, row in corr_df.iterrows():
                lowcut_vals = lowcut_ew[str(row['Line'])]
                opt_ew = [lowcut[1] for lowcut in lowcut_vals if lowcut[0] == row['Lowercut']]
                if len(opt_ew) == 0:
                    opt_ew = np.nan
                else:
                    opt_ew = opt_ew[0] - float(row['Offset'])
                out_df.loc[-1] = [float(row['Line']), opt_ew, row['Uncertainty']]  # adding a row
                out_df.index = out_df.index + 1  # shifting index
                out_df = out_df.sort_index()  # sorting by index
        out_df.to_csv("data/equiv_widths/{}".format(out_file), sep=" ", index=False, header=True, columns=["Line","EW","Uncertainty"])


if __name__ == "__main__":
    calc_ew("data/tame_outputs/*", "tame_linecorr.csv")
