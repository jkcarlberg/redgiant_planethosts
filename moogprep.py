import glob
import pandas as pd
import numpy as np

"""
1) Read in .ew file and cluster_fe_lines.csv
2) Match equivalent widths with fe_lines (based on wavelength)
2) Output a MOOG appropriate file containing: Wavelength    Ion     eP      Log-gf                  EW
"""


def moogprep(ew_file, output_dir, fe_line_file="cluster_fe_lines.csv"):
    clust, star = ew_file.split("/")[-1].split("_")[0:2]
    f_name = clust + "_" + star[0:-3]
    with open(output_dir+f_name+".txt", "w") as f:
        f.write(f_name+"\n")
        fe_lines = pd.read_csv(fe_line_file).loc[:, :'Log-gf']
        ew_list = pd.read_csv(ew_file, delim_whitespace=True).loc[:, :'EW']

        for line in fe_lines.iterrows():
            wav, ion, ep, log_gf = line[1]
            crossref = ew_list.loc[ew_list['Line'] == wav]['EW']

            # Avoid lines that didn't have TAME output
            if len(crossref) == 0:
                continue

            # Avoid lines that had a Nan TAME output
            elif np.isnan(float(crossref)):
                continue

            else:
                ew = float(crossref)
                file_line = "  {:.2f}\t{:.1f}\t{:.2f}\t{:.2f}\t\t\t{:.2f}".format(wav, ion, ep, log_gf, ew)
                f.write(file_line)
                f.write("\n")


if __name__ == "__main__":
    known = glob.glob("data/ew_known/equiv_widths/*.ew")
    for spec in known:
        print(spec)
        moogprep(spec, "data/ew_known/moog_inputs/")

    rrs = glob.glob("data/oc_rrs/equiv_widths/*.ew")
    for spec in rrs:
        print(spec)
        moogprep(spec, "data/oc_rrs/moog_inputs/")

    ctrl = glob.glob("data/ph_ctrl_stars/equiv_widths/*.ew")
    for spec in ctrl:
        print(spec)
        moogprep(spec, "data/ph_ctrl_stars/moog_inputs/")
