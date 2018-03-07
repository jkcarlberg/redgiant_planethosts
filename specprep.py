#!/usr/bin/python

import numpy as np
from astropy.io import fits
import os
import csv
import pandas as pd
import glob


class SpecPrep:

    def __init__(self, files, path='.', outdir='tame-1.1.0/', gen_ew_file=True):
        self.files = files
        self.path = path
        self.outdir = outdir
        self.gen_ew_file = gen_ew_file
        self.cluster_list_corr = "cluster_fe_lines.csv"
        self.cluster_list_orig = "cluster_fe_lines_orig.csv"
        self.file_glob = glob.glob(os.path.join(path, self.files))
        for filename in self.file_glob:
            print(filename)
            has_measurement = self.linelist_from_csv(filename, outdir=self.outdir, gen_ew_file=self.gen_ew_file)
            if has_measurement:
                self.onedspec_fits(filename, path=self.path, outdir=self.outdir)
                self.spec_lpx(filename, path=self.outdir, outdir=self.outdir)


    @staticmethod
    def onedspec_fits(filename, path='.', outdir='.'):
        """Calculate wavelength solutions for 1-d Spectra"""
        with fits.open(os.path.join(path, filename)) as hdulist:
            # Grab relevant header values
            cdelt1 = hdulist[0].header["CDELT1"]
            cd1_1 = hdulist[0].header["CD1_1"]
            crval1 = hdulist[0].header["CRVAL1"]
            crpix1 = hdulist[0].header["CRPIX1"]
            dc_flag = hdulist[0].header["DC-FLAG"]

            # Find nonzero delta value
            if cdelt1 != 0:
                cd1 = cdelt1
            elif cd1_1 != 0:
                cd1 = cd1_1
            else:
                print("Error: No delta lambda found.")
                return

            # Create index array for data (idx+1 for python -> IRAF indexing)
            pix = np.array([idx+1 for idx, val in enumerate(hdulist[0].data)])
            if dc_flag == 0:       # Linear sampling
                wave = crval1+cd1*(pix-crpix1)
            elif dc_flag == 1:     # Log-Linear sampling
                wave = 10.0**(crval1+cd1*(pix-crpix1))
            else:
                print("DC-Flag is non-binary")
                return

            # Write data to new fits file
            fluxcol = fits.Column(name='FLUX', format='E', array=hdulist[0].data)
            wavelcol = fits.Column(name='WAVEL', format='E', array=wave)
            wav_hdu = fits.BinTableHDU.from_columns([fluxcol, wavelcol], name="WAV")
            hdulist.append(wav_hdu)

            filename = filename.split('/')[-1]
            hdulist.writeto(os.path.join(outdir, filename.split('.')[0]+"_wavsoln.fits"),
                            overwrite=True)

    @staticmethod
    def spec_lpx(filename, path='.', outdir='.'):
        """Generate a spectrum text file for use with TAME"""
        filename = filename.split('/')[-1]
        with fits.open(os.path.join(path, filename.split('.')[0]+"_wavsoln.fits")) as hdulist:
            wavelength = hdulist['WAV'].data['WAVEL']
            flux = hdulist['WAV'].data['FLUX']

            with open(os.path.join(outdir, filename.split('.')[0]+'.lpx'), 'w') as f:
                writer = csv.writer(f, delimiter=' ')
                writer.writerows(zip(wavelength, flux))

    def linelist_from_csv(self, filename, outdir='.', gen_ew_file=True):
        """Generate a linelist for a file from the cluster csv list"""
        df_corr = pd.read_csv(self.cluster_list_corr)
        df_orig = pd.read_csv(self.cluster_list_orig, skiprows=1)
        print(filename)
        filename = filename.split('/')[-1]
        star_num = filename.split('_')[1][:-3]  # Isolate star number and remove 'red'
        print(star_num)
        columns = ['Wavelength', 'Ion', 'eP', 'Log-gf', star_num]
        has_measurement = False

        if star_num in df_corr.keys():
            print("Found Star in Redone Spreadsheet")
            df = df_corr[columns]
            has_measurement = True
        elif star_num in df_orig.keys():
            print("Found Star in Original Spreadsheet")
            df = df_orig[columns]
            has_measurement = True
        else:
            print("No Equivalent Width measurements taken for Star. Exiting.")
            return has_measurement

        # Mask skipped wavelengths
        m = np.isnan(df[star_num]) == False
        mask = [row.all() for row in (df.where(m, df) == df.mask(~m, df)).values]

        masked_lines = df[mask][columns[:-1]].values
        masked_ew = df[mask][columns].values
        with open(os.path.join(outdir, filename.split('.')[0]+'.lines'), 'w') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerows(masked_lines)

        if gen_ew_file:
            with open(os.path.join(outdir, filename.split('.')[0]+'.ew'), 'w') as f:
                writer = csv.writer(f, delimiter=' ')
                writer.writerows(masked_ew)

        return has_measurement


if __name__ == "__main__":
    pass
