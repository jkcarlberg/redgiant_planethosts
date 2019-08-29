#!/usr/bin/python

import numpy as np
import json
import pandas as pd
import glob
from ast import literal_eval


def calc_ew(file_list, linecorr):
    """Take the tame json output files and apply linecorr adjustments to extract calibrated equivalent widths"""

    # Read in the files
    files = glob.glob(file_list)
    corr_df = pd.read_csv(linecorr, delim_whitespace=True)
    bad_count = 0
    total_count = 0
    #Iterate over file list
    for file in files:
        fname = file.split('/')[-1].split('.')[0]
        print(fname)
        if "ngc2204_3321" in fname:
            continue
        out_file = fname+".ew"
        out_df = pd.DataFrame({"Line": [], "EW": [], "Uncertainty": [], "Linecenter": []})
        out_df = out_df[["Line", "EW", "Uncertainty", "Linecenter"]]

        #Read in json file
        with open(file) as json_file:
            lowcut_ew = json.load(json_file)
            print(len(lowcut_ew.keys()))
            #Iterate over lines
            for index, row in corr_df.iterrows():

                all_meas = literal_eval(row['Calibration Values'])
                try:
                    lowcut_vals = lowcut_ew[str(row['Line'])]
                except KeyError:
                    out_df.loc[-1] = [str(row['Line']), np.nan, np.nan, np.nan]  # adding a row
                    out_df.index = out_df.index + 1  # shifting index
                    out_df = out_df.sort_index()  # sorting by index
                    total_count += 1
                    continue

                good_meas = [meas for meas in lowcut_vals if abs(meas[2]-row['Line']) < 0.05]
                bad_meas = [meas for meas in lowcut_vals if abs(meas[2]-row['Line']) > 0.05]
                if len(good_meas) == 0: #If there are no close measurements
                    print("Skipped Line at {} in {}".format(row['Line'], fname))
                    out_df.loc[-1] = [float(row['Line']), np.nan, np.nan,
                                      np.nan]  # adding a row
                    out_df.index = out_df.index + 1  # shifting index
                    out_df = out_df.sort_index()  # sorting by index
                    bad_count += 1
                    total_count += 1

                else:
                    opt_arg = np.argmin(np.array([abs(lowcut[0] - row['Lowercut']) for lowcut in good_meas]))
                    best_lowcut = good_meas[opt_arg][0]
                    cal_arg = np.argmin(np.array([abs(float(lowcut[0]) - float(best_lowcut)) for lowcut in all_meas]))
                    opt_ew = good_meas[opt_arg][1] - all_meas[cal_arg][2]
                    out_df.loc[-1] = [float(row['Line']), opt_ew, all_meas[cal_arg][1],
                                      lowcut_vals[opt_arg][2]]  # adding a row
                    out_df.index = out_df.index + 1  # shifting index
                    out_df = out_df.sort_index()  # sorting by index
                    total_count += 1

        out_df.to_csv("data/ph_ctrl_stars/equiv_widths/{}".format(out_file), sep=" ", index=False, header=True, columns=["Line","EW", "Uncertainty", "Linecenter"])
    print(bad_count, total_count, bad_count/total_count)

if __name__ == "__main__":
    calc_ew("data/ph_ctrl_stars/tame_outputs/*.json", "tame_linecorr_v2.csv")
