#!/usr/bin/env python
"""
Collate analysis results for PSF FFT testing.

Hazen 10/17
"""
import glob

import storm_analysis.diagnostics.collate as collateResults

import storm_analysis.diagnostics.psf_fft.settings as settings

def collate():
    dirs = sorted(glob.glob("test*"))

    if(len(dirs) == 0):
        print("No test directories found.")
        exit()

    collateResults.collateSpliner(dirs, settings)


if (__name__ == "__main__"):
    collate()
    
