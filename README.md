# redgiant_planethosts
Heavy Metal Abundances of Red Giant Stars That Host Planets

Python EQW Fitting:
* visualize_fit.ipynb:
    * A notebook that contains the ipywidget used for interactive assessment of equivalent width fitting on star/line combinations.
    * Useful for investigating discrepant eqw measurements and tuning line parameters
    * ipywidgets has some extra steps to get working with jupyter lab, should work out of the box with jupyter notebooks
    * Notebook also has notes on which lines were checked, what custom line profiles were set per line, and which lines were thrown out
* auto_eqw.ipynb:
    * The notebook that lays out the EQW fitting workflow that is used in this project, going through pyspeckit and support scripts like c_normalize
    * Several examples of specific lines 
* auto_eqw_all.ipynb:
    * A notebook that fits equivalent widths to a line list for a set of spectrum
    * More of a test notebook for the script implementation in pycalc_ew.py
* c_normalize.py: 
    * A script that normalizes a spectrum, adaptation of Joleens idl script
    * Used as a part of the EQW workflow
* create_yaml_all.py:
    * contains the hardcoded line parameters that specifies the optimal fitting parameters for each line, also contained is a default setting for all lines not listed
    * the script exports the dictionary to a yaml file for use with the fitting code
* pycalc_ew.py:
    * The main script that generates EQWs for the desired lines in a set of spectrum.
TESS Crossref:
* TESS_crossref.ipynb:
    * main notebook for using mast and lightkurve to read in and analyze TESS light curves
