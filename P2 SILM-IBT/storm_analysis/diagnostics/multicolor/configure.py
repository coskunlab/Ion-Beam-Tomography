#!/usr/bin/env python
"""
Configure folder for Multicolor testing.

Hazen 01/18
"""
import argparse
import inspect
import numpy
import os
import pickle
import subprocess

import storm_analysis
import storm_analysis.sa_library.parameters as parameters
import storm_analysis.sa_library.sa_h5py as saH5Py

import storm_analysis.simulator.background as background
import storm_analysis.simulator.camera as camera
import storm_analysis.simulator.drift as drift
import storm_analysis.simulator.photophysics as photophysics
import storm_analysis.simulator.psf as psf
import storm_analysis.simulator.simulate as simulate

import storm_analysis.sCMOS.scmos_analysis as scmos

import storm_analysis.diagnostics.multicolor.settings as settings


def testingParametersSCMOS():
    """
    Create a sCMOS parameters object.
    """
    params = parameters.ParametersSCMOS()

    params.setAttr("max_frame", "int", -1)    
    params.setAttr("start_frame", "int", -1)    
    
    params.setAttr("background_sigma", "float", 8.0)
    params.setAttr("camera_calibration", "filename", "calib.npy")
    params.setAttr("find_max_radius", "int", 5)
    params.setAttr("foreground_sigma", "float", 1.5)
    params.setAttr("iterations", "int", settings.iterations)
    params.setAttr("model", "string", "2dfixed")
    params.setAttr("pixel_size", "float", settings.pixel_size)
    params.setAttr("sigma", "float", 150.0/settings.pixel_size)
    params.setAttr("threshold", "float", 6.0)

    # Don't do tracking.
    params.setAttr("descriptor", "string", "1")
    params.setAttr("radius", "float", "0.0")

    # Don't do drift-correction.
    params.setAttr("d_scale", "int", 2)
    params.setAttr("drift_correction", "int", 0)
    params.setAttr("frame_step", "int", 500)
    params.setAttr("z_correction", "int", 0)
    
    return params


def testingParametersMC():
    """
    Create a Multiplane parameters object.
    """
    params = parameters.ParametersMultiplaneArb()

    params.setAttr("max_frame", "int", -1)    
    params.setAttr("start_frame", "int", -1)
    
    params.setAttr("background_sigma", "float", 8.0)
    params.setAttr("find_max_radius", "int", 2)
    params.setAttr("independent_heights", "int", settings.independent_heights)
    params.setAttr("iterations", "int", settings.iterations)
    params.setAttr("mapping", "filename", "map.map")
    params.setAttr("no_fitting", "int", 0)
    params.setAttr("pixel_size", "float", settings.pixel_size)
    params.setAttr("sigma", "float", 1.5)
    params.setAttr("threshold", "float", 6.0)
    params.setAttr("weights", "filename", "weights.npy")
    params.setAttr("z_value", "float-array", settings.z_value)

    params.setAttr("channel0_cal", "filename", "calib.npy")
    params.setAttr("channel1_cal", "filename", "calib.npy")
    params.setAttr("channel2_cal", "filename", "calib.npy")
    params.setAttr("channel3_cal", "filename", "calib.npy")

    params.setAttr("channel0_ext", "string", "_c1.dax")
    params.setAttr("channel1_ext", "string", "_c2.dax")
    params.setAttr("channel2_ext", "string", "_c3.dax")
    params.setAttr("channel3_ext", "string", "_c4.dax")

    params.setAttr("channel0_offset", "int", 0)
    params.setAttr("channel1_offset", "int", 0)
    params.setAttr("channel2_offset", "int", 0)
    params.setAttr("channel3_offset", "int", 0)

    params.setAttr("spline0", "filename", "c1_psf.spline")
    params.setAttr("spline1", "filename", "c2_psf.spline")
    params.setAttr("spline2", "filename", "c3_psf.spline")
    params.setAttr("spline3", "filename", "c4_psf.spline")    

    # Do tracking (localization color analysis depends on the tracks).
    params.setAttr("descriptor", "string", "1")
    params.setAttr("radius", "float", "1.0")

    params.setAttr("max_z", "float", str(0.001 * settings.psf_z_range))
    params.setAttr("min_z", "float", str(-0.001 * settings.psf_z_range))
    
    # Don't do drift-correction.
    params.setAttr("d_scale", "int", 2)
    params.setAttr("drift_correction", "int", 0)
    params.setAttr("frame_step", "int", 500)
    params.setAttr("z_correction", "int", 0)

    return params

def configure():
    # Get relevant paths.
    mm_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/micrometry/"
    mp_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/multi_plane/"
    sp_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/spliner/"

    # Create analysis XML files.
    #
    print("Creating XML files.")
    params = testingParametersSCMOS()
    params.toXMLFile("scmos.xml")

    params = testingParametersMC()
    params.toXMLFile("multicolor.xml")
    
    # Useful variables
    aoi_size = int(settings.psf_size/2)+1

    # Create sCMOS data and HDF5 files we'll need for the simulation.
    #
    if True:

        # Create sCMOS camera calibration files.
        #
        numpy.save("calib.npy", [numpy.zeros((settings.y_size, settings.x_size)) + settings.camera_offset,
                                 numpy.ones((settings.y_size, settings.x_size)) * settings.camera_variance,
                                 numpy.ones((settings.y_size, settings.x_size)) * settings.camera_gain,
                                 numpy.ones((settings.y_size, settings.x_size)),
                                 2])
    
        # Create localization on a grid file.
        #
        print("Creating gridded localizations.")
        sim_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/simulator/"
        subprocess.call(["python", sim_path + "emitters_on_grid.py",
                         "--bin", "grid_list.hdf5",
                         "--nx", str(settings.nx),
                         "--ny", str(settings.ny),
                         "--spacing", "20",
                         "--zrange", str(settings.test_z_range),
                         "--zoffset", str(settings.test_z_offset)])

        # Create randomly located localizations file (for STORM movies).
        #
        print("Creating random localizations.")
        subprocess.call(["python", sim_path + "emitters_uniform_random.py",
                         "--bin", "random_storm.hdf5",
                         "--density", "1.0",
                         "--margin", str(settings.margin),
                         "--sx", str(settings.x_size),
                         "--sy", str(settings.y_size),
                         "--zrange", str(settings.test_z_range)])

        # Create randomly located localizations file (for mapping measurement).
        #
        print("Creating random localizations.")
        subprocess.call(["python", sim_path + "emitters_uniform_random.py",
                         "--bin", "random_map.hdf5",
                         "--density", "0.0003",
                         "--margin", str(settings.margin),
                         "--sx", str(settings.x_size),
                         "--sy", str(settings.y_size)])

        # Create sparser grid for PSF measurement.
        #
        print("Creating data for PSF measurement.")
        sim_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/simulator/"
        subprocess.call(["python", sim_path + "emitters_on_grid.py",
                         "--bin", "psf_list.hdf5",
                         "--nx", "6",
                         "--ny", "3",
                         "--spacing", "40"])


    ## This part makes / tests measuring the mapping.
    ##
    if True:
        print("Measuring mapping.")
    
        # Make localization files for simulations.
        #
        locs = saH5Py.loadLocalizations("random_map.hdf5")
        locs["z"][:] = 1.0e-3 * settings.z_planes[0]
        saH5Py.saveLocalizations("c1_random_map.hdf5", locs)
        for i in range(1,4):
            locs["x"] += settings.dx
            locs["y"] += settings.dy
            locs["z"][:] = settings.z_planes[i]
            saH5Py.saveLocalizations("c" + str(i+1) + "_random_map.hdf5", locs)

        # Make localization files for simulations.
        #
        locs = saH5Py.loadLocalizations("random_map.hdf5")
        locs["z"][:] = 1.0e-3 * settings.z_planes[0]
        saH5Py.saveLocalizations("c1_random_map.hdf5", locs)
        for i in range(1,4):
            locs["x"] += settings.dx
            locs["y"] += settings.dy
            locs["z"][:] = settings.z_planes[i]
            saH5Py.saveLocalizations("c" + str(i+1) + "_random_map.hdf5", locs)
        
        # Make simulated mapping data.
        # 
        bg_f = lambda s, x, y, h5 : background.UniformBackground(s, x, y, h5, photons = 10)
        cam_f = lambda s, x, y, h5 : camera.SCMOS(s, x, y, h5, "calib.npy")
        pp_f = lambda s, x, y, h5 : photophysics.AlwaysOn(s, x, y, h5, 20000.0)
        psf_f = lambda s, x, y, i3 : psf.GaussianPSF(s, x, y, i3, settings.pixel_size)

        sim = simulate.Simulate(background_factory = bg_f,
                                camera_factory = cam_f,
                                photophysics_factory = pp_f,
                                psf_factory = psf_f,
                                x_size = settings.x_size,
                                y_size = settings.y_size)

        for i in range(4):
            sim.simulate("c" + str(i+1) + "_map.dax", "c" + str(i+1) + "_random_map.hdf5", 1)
    
        # Analyze simulated mapping data
        #
        for i in range(4):
            scmos.analyze("c" + str(i+1) + "_map.dax", "c" + str(i+1) + "_map.hdf5", "scmos.xml")

        # Measure mapping.
        #
        for i in range(3):
            subprocess.call(["python", mm_path + "micrometry.py",
                             "--locs1", "c1_map.hdf5",
                             "--locs2", "c" + str(i+2) + "_map.hdf5",
                             "--results", "c1_c" + str(i+2) + "_map.map",
                             "--no_plots"])

        # Merge mapping.
        #
        subprocess.call(["python", mm_path + "merge_maps.py",
                         "--results", "map.map",
                         "--maps", "c1_c2_map.map", "c1_c3_map.map", "c1_c4_map.map"])
        
        # Print mapping.
        #
        if True:
            print("Mapping is:")
            subprocess.call(["python", mp_path + "print_mapping.py",
                             "--mapping", "map.map"])
            print("")

        # Check that mapping is close to what we expect (within 5%).
        #
        with open("map.map", 'rb') as fp:
            mappings = pickle.load(fp)

        for i in range(3):
            if not numpy.allclose(mappings["0_" + str(i+1) + "_x"], numpy.array([settings.dx*(i+1), 1.0, 0.0]), rtol = 0.05, atol = 0.05):
                print("X mapping difference for channel", i+1)
            if not numpy.allclose(mappings["0_" + str(i+1) + "_y"], numpy.array([settings.dy*(i+1), 0.0, 1.0]), rtol = 0.05, atol = 0.05):
                print("Y mapping difference for channel", i+1)
    

    ## This part measures / test the PSF measurement.
    ##
    if True:

        # Create drift file, this is used to displace the localizations in the
        # PSF measurement movie.
        #
        dz = numpy.arange(-settings.psf_z_range, settings.psf_z_range + 0.05, 0.01)
        drift_data = numpy.zeros((dz.size, 3))
        drift_data[:,2] = dz
        numpy.savetxt("drift.txt", drift_data)

        # Also create the z-offset file.
        #
        z_offset = numpy.ones((dz.size, 2))
        z_offset[:,1] = dz
        numpy.savetxt("z_offset.txt", z_offset)

        # Create simulated data for PSF measurements.
        #
        bg_f = lambda s, x, y, h5 : background.UniformBackground(s, x, y, h5, photons = 10)
        cam_f = lambda s, x, y, h5 : camera.SCMOS(s, x, y, h5, "calib.npy")
        drift_f = lambda s, x, y, h5 : drift.DriftFromFile(s, x, y, h5, "drift.txt")
        pp_f = lambda s, x, y, h5 : photophysics.AlwaysOn(s, x, y, h5, 20000.0)
        psf_f = lambda s, x, y, h5 : psf.PupilFunction(s, x, y, h5, settings.pixel_size, [])

        sim = simulate.Simulate(background_factory = bg_f,
                                camera_factory = cam_f,
                                drift_factory = drift_f,
                                photophysics_factory = pp_f,
                                psf_factory = psf_f,
                                x_size = settings.x_size,
                                y_size = settings.y_size)

        if True:
            for i in range(4):
                sim.simulate("c" + str(i+1) + "_zcal.dax",
                             "c" + str(i+1) + "_random_map.hdf5",
                             dz.size)
        
        # Get localizations to use for PSF measurement.
        #
        subprocess.call(["python", mp_path + "psf_localizations.py",
                         "--bin", "c1_map_ref.hdf5",
                         "--map", "map.map",
                         "--aoi_size", str(aoi_size)])
    
        # Create PSF z stacks.
        #
        for i in range(4):
            subprocess.call(["python", mp_path + "psf_zstack.py",
                             "--movie", "c" + str(i+1) + "_zcal.dax",
                             "--bin", "c1_map_ref_c" + str(i+1) + "_psf.hdf5",
                             "--zstack", "c" + str(i+1) + "_zstack",
                             "--scmos_cal", "calib.npy",
                             "--aoi_size", str(aoi_size)])

        # Measure PSF.
        #
        for i in range(4):
            subprocess.call(["python", mp_path + "measure_psf.py",
                             "--zstack", "c" + str(i+1) + "_zstack.npy",
                             "--zoffsets", "z_offset.txt",
                             "--psf_name", "c" + str(i+1) + "_psf_normed.psf",
                             "--z_range", str(settings.psf_z_range),
                             "--normalize"])


    ## This part creates the splines.
    ##
    if True:
        print("Measuring Splines.")
        for i in range(4):
            subprocess.call(["python", sp_path + "psf_to_spline.py",
                             "--psf", "c" + str(i+1) + "_psf_normed.psf",
                             "--spline", "c" + str(i+1) + "_psf.spline",
                             "--spline_size", str(int(settings.psf_size/2))])
        
            
    ## This part measures the Cramer-Rao weights.
    ##
    if True:
        print("Calculating weights.")
        subprocess.call(["python", mp_path + "plane_weighting.py",
                         "--background", str(settings.photons[0][0]),
                         "--photons", str(settings.photons[0][1]),
                         "--output", "weights.npy",
                         "--xml", "multicolor.xml",
                         "--no_plots"])


if (__name__ == "__main__"):
    configure()
    
