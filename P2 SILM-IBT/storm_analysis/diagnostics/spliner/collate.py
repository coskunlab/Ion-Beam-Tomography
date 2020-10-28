#!/usr/bin/env python
"""
Collate analysis results for Spliner testing.

Hazen 09/17
"""
import glob

import storm_analysis.diagnostics.collate as collateResults

import storm_analysis.diagnostics.spliner.settings as settings

def collate():
    dirs = sorted(glob.glob("test*"))

    if(len(dirs) == 0):
        print("No test directories found.")
        return

    collateResults.collateSpliner(dirs, settings)

if (__name__ == "__main__"):
    collate()
    
