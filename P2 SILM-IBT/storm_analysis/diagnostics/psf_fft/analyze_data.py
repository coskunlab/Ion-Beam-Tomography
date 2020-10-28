#!/usr/bin/env python
"""
Analyze test data using PSF FFT.

Hazen 10/17
"""
import glob
import os
import time

import storm_analysis.psf_fft.psffft_analysis as psffftAna

def analyzeData():
    dirs = sorted(glob.glob("test*"))

    for a_dir in dirs:
        print()
        print("Analyzing:", a_dir)
        print()
    
        mlist = a_dir + "/test.hdf5"

        # Remove stale results, if any.
        if os.path.exists(mlist):
            os.remove(mlist)

        # Run analysis.
        start_time = time.time()
        psffftAna.analyze(a_dir + "/test.dax", mlist, "psf_fft.xml")
        stop_time = time.time()

        # Save timing results.
        print("Analysis completed in {0:.2f} seconds".format(stop_time - start_time))

        with open(a_dir + "/timing.txt", "w") as fp:
            fp.write(str(stop_time - start_time) + "\n")


if (__name__ == "__main__"):
    analyzeData()
    
