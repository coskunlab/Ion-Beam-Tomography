#!/usr/bin/env python
"""
Base classes for deconvolving images using compressed sensing
approaches such as FISTA or ADMM.

Hazen 2/18
"""
import numpy

import storm_analysis.sa_library.cs_decon_utilities_c as csDeconUtilsC
import storm_analysis.sa_library.fitting as fitting
import storm_analysis.simulator.draw_gaussians_c as dg


class CSDecon(object):
    """
    Base class for compressed sensing deconvolution.
    """
    def __init__(self, image_size, psf_object, number_zvals):
        self.background = numpy.zeros(image_size)
        self.cs_solver = None
        self.image_size = image_size
        self.new_image = None
        self.psf_object = psf_object

        # Calculate z values to use if 3D.
        if (self.psf_object.getType() == "3D") and (number_zvals > 1):
            self.z_min = self.psf_object.getZMin() + 1.0
            self.z_max = self.psf_object.getZMax() - 1.0
            z_step = (self.z_max - self.z_min)/float(number_zvals - 1.0)        
            self.zvals = []
            for i in range(number_zvals):
                self.zvals.append(self.z_min + float(i) * z_step)
        else:
            self.z_min = 0.0
            self.z_max = 1.0
            self.zvals = [0.0]

    def cleanup(self):
        self.cs_solver.cleanup()

    def createPSFs(self, normalize = True):
        psfs = numpy.zeros((self.image_size[0], self.image_size[1], len(self.zvals)))
        for i in range(len(self.zvals)):
            psfs[:,:,i] = self.psf_object.getPSF(self.zvals[i],
                                                 shape = self.image_size,
                                                 normalize = normalize)
        return psfs
            
    def decon(self, iterations, cs_lambda, verbose = False):
        for i in range(iterations):
            if verbose and ((i%10) == 0):
                print(i, self.cs_solver.l2Error())
            self.cs_solver.iterate(cs_lambda)

    def getPeaks(self, threshold, margin):
        """
        Extract peaks from the deconvolved image and create
        an array that can be used by a peak fitter.
        """
        fx = self.getXVector()

        fd_peaks = csDeconUtilsC.getPeaks(fx, threshold, margin)

        peaks = {"x" : fd_peaks[:,2],
                 "y" : fd_peaks[:,1]}

        if (fx.shape[2] > 1):

            # Initial z as the range 0.0 - 1.0.
            temp_z = fd_peaks[:,3]/(float(fx.shape[2])-1.0)

            # Convert z to nanometers.
            peaks["z"] = (self.z_max - self.z_min)*temp_z + self.z_min
            
        else:
            peaks["z"] = numpy.zeros(peaks["x"].size)
        
        return peaks
        
    def getXVector(self):
        return self.cs_solver.getXVector()

    def getZRange(self):
        return [self.z_min, self.z_max]

    def newBackground(self, background):
        no_bg_image = self.new_image - background
        self.cs_solver.newImage(no_bg_image)
        
    def newImage(self, image):
        self.new_image = image


class GaussianPSFFunction(fitting.PSFFunction):
    """
    A Gaussian PSF object, mostly for decon testing.
    """
    def __init__(self, res = 5, sigma = None, **kwds):
        super(GaussianPSFFunction, self).__init__(**kwds)

        self.res = res
        self.sigma = sigma

    def getPSF(self, z_value, shape = None, normalize = False):
        cx = numpy.array([0.5*float(shape[0])])
        cy = numpy.array([0.5*float(shape[1])])
        return dg.drawGaussiansXY(shape, cx, cy, sigma = self.sigma, res = self.res)
        
    def getType(self):
        return "2D"


#
# The MIT License
#
# Copyright (c) 2016 Zhuang Lab, Harvard University
# Copyright (c) 2018 Babcock Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
