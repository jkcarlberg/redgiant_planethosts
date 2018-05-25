#!/usr/bin/python

import json
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import matplotlib as mpl
from astropy.stats import sigma_clip
from scipy.stats import iqr
import csv

plt.style.use('seaborn-white')
mpl.rcParams.update({'font.size': 16})

# Select Datasets and extract equivalent widths
outputs = glob.glob("data/tame_outputs/*.json")
by_hand = glob.glob("data/tame_inputs/*.ew")
lc_range = np.arange(0.95, 0.995, 0.0001)
len_range = 10


d = {'JSON File': outputs, 'By-Hand File': by_hand}
disp_df = pd.DataFrame(data=d)

# Find optimal lowercut value
write_out = True

with open(outputs[0]) as jsonfile:
    jsondata = json.load(jsonfile)
    key = list(jsondata.keys())[2]
    lowcuts = [cut for cut, ew, center in jsondata[key]]
    line_list = list(jsondata.keys())
    line_list = np.array(sorted(np.array(line_list).astype(float))).astype(str)

if write_out:
    csvfile = open("tame_linecorr_v2.csv", "w")
    csvwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["Line", "Lowercut", "Uncertainty", "Offset", "Calibration Values"])
solns_dev = []
closest_dev = []
closest_pdiffs = []

line_dict = {}
for line in line_list[:]:
    pdiff_all = []
    hand_all = []
    for i in range(len(outputs)):
        if 'ngc2204_3321red' in outputs[i]:
            continue
        with open(outputs[i]) as jsonfile, open(by_hand[i]) as ewfile:
            jsondata = json.load(jsonfile)
            handdata = pd.read_csv(ewfile, delim_whitespace=True, header=None)[[0, 4]]
            hand_dict = dict(zip([str(i) for i in handdata[0].tolist()], handdata[4].tolist()))
            key = line
            lowercut = [cut for cut, ew, center in jsondata[key]]
            ew_meas = [ew for cut, ew, center in jsondata[key]]
            # print(outputs[i])
            # print(ew_meas)
            # print(hand_dict[key])

            label = disp_df['JSON File'][i].split('/')[-1].split('.')[0]
            if hand_dict[key] == 0:
                continue
            if len(lowercut) < len_range:
                continue
            # plt.plot(lowercut,ew_pdiff,'.',color='k')
            ew_pdiff = ((np.array(ew_meas) - hand_dict[key]) / hand_dict[key]) * 100
            ew_absdiff = np.array(ew_meas) - hand_dict[key]
            pdiff_all.append(ew_absdiff)
            hand_all.append(hand_dict[key])

    pdiff_all = np.array(pdiff_all, dtype='object').T
    # print(hand_all)

    # Sigma Clip
    sigma = 5
    pdiff_sclip = [np.ma.compressed(sigma_clip(np.array(pdiff_all[lowcuts.index(lc_val)]).astype(float), sigma=sigma))
                   for lc_val in lowcuts]
    # print(len(pdiff_all))

    avg_pdiffs = [np.median(pdiff_sclip[lowcuts.index(lc_val)]) for lc_val in lowcuts]
    std_pdiffs = [np.median(abs(pdiff_sclip[lowcuts.index(lc_val)])) for lc_val in lowcuts]
    # median of abs value of the diff

    best_lowcut = lowcuts[np.argmin(std_pdiffs)]  # Best lowcut is solution with smallest spread (not solution that has the closest percent difference)
    pdiff_offset = avg_pdiffs[np.argmin(std_pdiffs)]  # The mean percent difference associated with the chosen lowcut value is the offset value

    line_dict[line] = (best_lowcut, np.min(std_pdiffs), pdiff_offset, np.mean(hand_all))
    calibration = list(zip(lowcuts, np.round(np.array(std_pdiffs)*1.5, 2), np.round(avg_pdiffs, 2)))
    print(calibration)
    if write_out:
        csvwriter.writerow([line, best_lowcut, np.min(std_pdiffs) * 1.5, pdiff_offset, calibration])


if write_out:
    csvfile.close()

# END