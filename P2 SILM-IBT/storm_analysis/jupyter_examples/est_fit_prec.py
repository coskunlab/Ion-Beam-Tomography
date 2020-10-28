#!/usr/bin/env python
"""
Configure folder for estimating fitting precision example.

Hazen 08/18
"""
import inspect
import os

import storm_analysis
import storm_analysis.sa_library.parameters as parameters
import storm_analysis.sa_library.sa_h5py as saH5Py

import storm_analysis.simulator.background as background
import storm_analysis.simulator.camera as camera
import storm_analysis.simulator.emitters_on_grid as emittersOnGrid
import storm_analysis.simulator.emitters_uniform_random as emittersUniformRandom
import storm_analysis.simulator.photophysics as photophysics
import storm_analysis.simulator.psf as psf
import storm_analysis.simulator.simulate as simulate

bg = 20
camera_gain = 1.0
camera_offset = 100.0
margin = 5
model = "2dfixed"
nx = 12
ny = 10
pixel_size = 100.0
signal = 2000
x_size = 256
y_size = 256


def createParametersFile():
    """
    Create a 3D-DAOSTORM parameters file.
    """
    params = parameters.ParametersDAO()

    params.setAttr("max_frame", "int", -1)    
    params.setAttr("start_frame", "int", -1)
    
    params.setAttr("background_sigma", "float", 8.0)
    params.setAttr("camera_gain", "float", camera_gain)
    params.setAttr("camera_offset", "float", camera_offset)
    params.setAttr("find_max_radius", "int", 5)
    params.setAttr("foreground_sigma", "float", 1.0)
    params.setAttr("iterations", "int", 20)
    params.setAttr("model", "string", model)
    params.setAttr("pixel_size", "float", pixel_size)
    params.setAttr("roi_size", "int", 9)
    params.setAttr("sigma", "float", 1.5)
    params.setAttr("threshold", "float", 6.0)

    # Z fitting.
    params.setAttr("do_zfit", "int", 0)

    params.setAttr("cutoff", "float", 0.0)    
    params.setAttr("max_z", "float", 0.5)
    params.setAttr("min_z", "float", -0.5)
    params.setAttr("z_value", "float", 0.0)
    params.setAttr("z_step", "float", 0.001)

    params.setAttr("wx_wo", "float", 300.0)
    params.setAttr("wx_c", "float", 150.0)
    params.setAttr("wx_d", "float", 400.0)
    params.setAttr("wxA", "float", 0.0)
    params.setAttr("wxB", "float", 0.0)
    params.setAttr("wxC", "float", 0.0)
    params.setAttr("wxD", "float", 0.0)

    params.setAttr("wy_wo", "float", 300.0)
    params.setAttr("wy_c", "float", -150.0)
    params.setAttr("wy_d", "float", 400.0)
    params.setAttr("wyA", "float", 0.0)
    params.setAttr("wyB", "float", 0.0)
    params.setAttr("wyC", "float", 0.0)
    params.setAttr("wyD", "float", 0.0)

    # Do tracking.
    params.setAttr("descriptor", "string", "1")
    params.setAttr("radius", "float", "0.5")

    # Do drift-correction.
    params.setAttr("d_scale", "int", 2)
    params.setAttr("drift_correction", "int", 1)
    params.setAttr("frame_step", "int", 500)
    params.setAttr("z_correction", "int", 0)
    
    params.toXMLFile("dao3d_analysis.xml")

def createLocalizationsGrid():
    emittersOnGrid.emittersOnGrid("grid_locs.hdf5", nx, ny, 1.5, 20, 0.0, 0.0)

def createLocalizationsRandom():
    emittersUniformRandom.emittersUniformRandom("random_locs.hdf5", 1.0, margin, x_size, y_size, 0.0) 

def createMovieGrid(n_frames):    
    bg_f = lambda s, x, y, i3 : background.UniformBackground(s, x, y, i3, photons = bg)
    cam_f = lambda s, x, y, i3 : camera.Ideal(s, x, y, i3, camera_offset)
    pp_f = lambda s, x, y, i3 : photophysics.AlwaysOn(s, x, y, i3, signal)
    psf_f = lambda s, x, y, i3 : psf.GaussianPSF(s, x, y, i3, pixel_size)

    sim = simulate.Simulate(background_factory = bg_f,
                            camera_factory = cam_f,
                            photophysics_factory = pp_f,
                            psf_factory = psf_f,
                            x_size = x_size,
                            y_size = y_size)
    
    sim.simulate("grid.tif", "grid_locs.hdf5", n_frames)

def createMovieRandom(n_frames):
    bg_f = lambda s, x, y, i3 : background.UniformBackground(s, x, y, i3, photons = bg)
    cam_f = lambda s, x, y, i3 : camera.Ideal(s, x, y, i3, camera_offset)
    pp_f = lambda s, x, y, i3 : photophysics.SimpleSTORM(s, x, y, i3, signal)
    psf_f = lambda s, x, y, i3 : psf.GaussianPSF(s, x, y, i3, pixel_size)

    sim = simulate.Simulate(background_factory = bg_f,
                            camera_factory = cam_f,
                            photophysics_factory = pp_f,
                            psf_factory = psf_f,
                            x_size = x_size,
                            y_size = y_size)
    
    sim.simulate("random.tif", "random_locs.hdf5", n_frames)
