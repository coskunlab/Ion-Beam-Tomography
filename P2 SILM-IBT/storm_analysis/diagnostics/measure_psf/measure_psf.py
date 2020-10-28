#!/usr/bin/env python
"""
Test PSF measurement scripts.

Hazen 01/18
"""
import inspect
import numpy
import os
import subprocess
import tifffile

import storm_analysis
import storm_analysis.sa_library.ia_utilities_c as iaUtilsC
import storm_analysis.sa_library.parameters as parameters
import storm_analysis.sa_library.sa_h5py as saH5Py

import storm_analysis.simulator.background as background
import storm_analysis.simulator.camera as camera
import storm_analysis.simulator.drift as drift
import storm_analysis.simulator.photophysics as photophysics
import storm_analysis.simulator.psf as psf
import storm_analysis.simulator.simulate as simulate

import storm_analysis.diagnostics.measure_psf.settings as settings


def psfDiffCheck(psf1, psf2, atol = 1.0e-3, rtol = 1.0e-6):
    is_different = False
    for i in range(psf1.shape[0]):
        #print(i, numpy.max(numpy.abs(psf1[i,:,:] - psf2[i,:,:])))
        if not numpy.allclose(psf1[i,:,:], psf2[i,:,:], atol = atol, rtol = rtol):
            is_different = True
            print("Difference of",
                  numpy.max(numpy.abs(psf1[i,:,:] - psf2[i,:,:])),
                  "at z section", i)

    if is_different:
        with tifffile.TiffWriter("diff.tif") as tf:
            for i in range(psf1.shape[0]):
                tf.save((psf1[i,:,:] - psf2[i,:,:]).astype(numpy.float32))
            
    return is_different

def measurePSF():
    
    # Create sparse random localizations for PSF measurement.
    #
    print("Creating random localization.")
    sim_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/simulator/"
    subprocess.call(["python", sim_path + "emitters_uniform_random.py",
                     "--bin", "sparse_random.hdf5",
                     "--density", "0.0002",
                     "--margin", str(settings.margin),
                     "--sx", str(settings.x_size),
                     "--sy", str(settings.y_size)])

    # Create sparser grid for PSF measurement.
    #
    print("Creating data for PSF measurement.")
    sim_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/simulator/"
    subprocess.call(["python", sim_path + "emitters_on_grid.py",
                     "--bin", "sparse_grid.hdf5",
                     "--nx", "8",
                     "--ny", "3",
                     "--spacing", "40"])

    # Create text files for PSF measurement.
    #
    locs = saH5Py.loadLocalizations("sparse_random.hdf5")
    [xf, yf] = iaUtilsC.removeNeighbors(locs["x"], locs["y"], 2.0 * ((settings.psf_size/2)+1))
    numpy.savetxt("sparse_random.txt", numpy.transpose(numpy.vstack((xf, yf))))
    
    locs = saH5Py.loadLocalizations("sparse_grid.hdf5")
    numpy.savetxt("sparse_grid.txt", numpy.transpose(numpy.vstack((locs['x'], locs['y']))))

    # Create drift file, this is used to displace the localizations in the
    # PSF measurement movie.
    #
    dz = numpy.arange(-settings.psf_z_range, settings.psf_z_range + 0.001, 0.010)
    drift_data = numpy.zeros((dz.size, 3))
    drift_data[:,2] = dz
    numpy.savetxt("drift.txt", drift_data)

    # Also create the z-offset file.
    #
    z_offset = numpy.ones((dz.size, 2))
    z_offset[:,1] = dz
    numpy.savetxt("z_offset.txt", z_offset)
    
    z_offset[:,0] = 0
    numpy.savetxt("z_offset_none_valid.txt", z_offset)
    
    # Create simulated data for PSF measurement.
    #
    bg_f = lambda s, x, y, i3 : background.UniformBackground(s, x, y, i3, photons = 10)
    cam_f = lambda s, x, y, i3 : camera.Ideal(s, x, y, i3, 100.)
    drift_f = lambda s, x, y, i3 : drift.DriftFromFile(s, x, y, i3, "drift.txt")
    pp_f = lambda s, x, y, i3 : photophysics.AlwaysOn(s, x, y, i3, 20000.0)
    psf_f = lambda s, x, y, i3 : psf.PupilFunction(s, x, y, i3, 100.0, settings.zmn)
    
    sim = simulate.Simulate(background_factory = bg_f,
                            camera_factory = cam_f,
                            drift_factory = drift_f,
                            photophysics_factory = pp_f,
                            psf_factory = psf_f,
                            x_size = settings.x_size,
                            y_size = settings.y_size)

    if True:
        sim.simulate("sparse_grid.tif", "sparse_grid.hdf5", dz.size)
        sim.simulate("sparse_random.tif", "sparse_random.hdf5", dz.size)

    # Measure the PSF using spliner/measure_psf_beads.py and multiplane/measure_psf.py
    #

    diff_detected = False

    # Grid.
    if True:

        # Remove old results.
        for elt in ["sparse_grid_beads.psf", "sparse_grid_hdf5_zo.psf",
                    "sparse_grid_hdf5.psf", "sparse_grid_hdf5_mp_zo.psf"]:
            if os.path.exists(elt):
                os.remove(elt)
        
        print("Measuring PSF (beads).")
        spliner_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/spliner/"
        subprocess.call(["python", spliner_path + "measure_psf_beads.py",
                         "--movie", "sparse_grid.tif",
                         "--zoffset", "z_offset.txt",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--beads", "sparse_grid.txt",
                         "--psf", "sparse_grid_beads.psf",
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])

        print("Measuring PSF (HDF5, with zoffset).")
        subprocess.call(["python", spliner_path + "measure_psf.py",
                         "--movie", "sparse_grid.tif",
                         "--bin", "sparse_grid_ref.hdf5",
                         "--psf", "sparse_grid_hdf5_zo.psf",
                         "--zoffset", "z_offset.txt",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])

        print("Measuring PSF (HDF5).")
        subprocess.call(["python", spliner_path + "measure_psf.py",
                         "--movie", "sparse_grid.tif",
                         "--bin", "sparse_grid_ref.hdf5",
                         "--psf", "sparse_grid_hdf5.psf",
                         "--zoffset", "",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])

        multiplane_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/multi_plane/"
        print("Measure PSF (multiplane).")
        subprocess.call(["python", multiplane_path + "psf_zstack.py",
                         "--movie", "sparse_grid.tif",
                         "--bin", "sparse_grid.hdf5",
                         "--zstack", "sparse_grid_zstack",
                         "--aoi_size", str(int(settings.psf_size/2)+1)])

        subprocess.call(["python", multiplane_path + "measure_psf.py",
                         "--zstack", "sparse_grid_zstack.npy",
                         "--zoffsets", "z_offset.txt",
                         "--psf_name", "sparse_grid_hdf5_mp_zo.psf",
                         "--z_range", str(settings.psf_z_range),
                         "--z_step", str(settings.psf_z_step),
                         "--normalize"])

        # Check that the PSFs are the same.
        psf_beads = numpy.load("sparse_grid_beads.psf")["psf"]
        psf_hdf5_zo = numpy.load("sparse_grid_hdf5_zo.psf")["psf"]
        psf_hdf5 = numpy.load("sparse_grid_hdf5.psf")["psf"]
        psf_hdf5_mp_zo = numpy.load("sparse_grid_hdf5_mp_zo.psf")["psf"]

        diff_detected = diff_detected or psfDiffCheck(psf_beads, psf_hdf5_zo)
        diff_detected = diff_detected or psfDiffCheck(psf_beads, psf_hdf5)

        # Here we are only checking they are close.
        if (settings.psf_size >= 20):
            diff_detected = diff_detected or psfDiffCheck(psf_beads, psf_hdf5_mp_zo, atol = 0.17, rtol = 0.17)

    # Grid, no valid z offsets. These are supposed to fail.
    #
    if True:
        print("Measuring PSF (beads).")
        spliner_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/spliner/"
        try:
            subprocess.check_output(["python", spliner_path + "measure_psf_beads.py",
                                     "--movie", "sparse_grid.tif",
                                     "--zoffset", "z_offset_none_valid.txt",
                                     "--aoi_size", str(int(settings.psf_size/2)+1),
                                     "--beads", "sparse_grid.txt",
                                     "--psf", "sparse_grid_beads.psf",
                                     "--zrange", str(settings.psf_z_range),
                                     "--zstep", str(settings.psf_z_step)])
        except subprocess.CalledProcessError:
            pass
        else:
            assert False, "spliner.measure_psf_beads did not fail!"

        print("Measuring PSF (HDF5, with zoffset).")
        try:
            subprocess.check_output(["python", spliner_path + "measure_psf.py",
                                     "--movie", "sparse_grid.tif",
                                     "--bin", "sparse_grid_ref.hdf5",
                                     "--psf", "sparse_grid_hdf5_zo.psf",
                                     "--zoffset", "z_offset_none_valid.txt",
                                     "--aoi_size", str(int(settings.psf_size/2)+1),
                                     "--zrange", str(settings.psf_z_range),
                                     "--zstep", str(settings.psf_z_step)])
        except subprocess.CalledProcessError:
            pass
        else:
            assert False, "spliner.measure_psf did not fail!"            

        multiplane_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/multi_plane/"
        print("Measure PSF (multiplane).")
        try:
            subprocess.check_output(["python", multiplane_path + "psf_zstack.py",
                                    "--movie", "sparse_grid.tif",
                                     "--bin", "sparse_grid.hdf5",
                                     "--zstack", "sparse_grid_zstack",
                                     "--aoi_size", str(int(settings.psf_size/2)+1)])

            subprocess.check_output(["python", multiplane_path + "measure_psf.py",
                                     "--zstack", "sparse_grid_zstack.npy",
                                     "--zoffsets", "z_offset_none_valid.txt",
                                     "--psf_name", "sparse_grid_hdf5_mp_zo.psf",
                                     "--z_range", str(settings.psf_z_range),
                                     "--z_step", str(settings.psf_z_step),
                                     "--normalize"])
        except subprocess.CalledProcessError:
            pass
        else:
            assert False, "multiplane PSF measurement did not fail!"

    # Random.
    if True:

        # Remove old results.
        for elt in ["sparse_random_beads.psf", "sparse_random_hdf5_zo.psf", "sparse_random_hdf5.psf"]:
            if os.path.exists(elt):
                os.remove(elt)
        
        print("Measuring PSF (beads).")
        spliner_path = os.path.dirname(inspect.getfile(storm_analysis)) + "/spliner/"
        subprocess.call(["python", spliner_path + "measure_psf_beads.py",
                         "--movie", "sparse_random.tif",
                         "--zoffset", "z_offset.txt",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--beads", "sparse_random.txt",
                         "--psf", "sparse_random_beads.psf",
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])

        print("Measuring PSF (HDF5, with zoffset).")
        subprocess.call(["python", spliner_path + "measure_psf.py",
                         "--movie", "sparse_random.tif",
                         "--bin", "sparse_random_ref.hdf5",
                         "--psf", "sparse_random_hdf5_zo.psf",
                         "--zoffset", "z_offset.txt",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])

        print("Measuring PSF (HDF5).")
        subprocess.call(["python", spliner_path + "measure_psf.py",
                         "--movie", "sparse_random.tif",
                         "--bin", "sparse_random_ref.hdf5",
                         "--psf", "sparse_random_hdf5.psf",
                         "--zoffset", "",
                         "--aoi_size", str(int(settings.psf_size/2)+1),
                         "--zrange", str(settings.psf_z_range),
                         "--zstep", str(settings.psf_z_step)])    

        psf_beads = numpy.load("sparse_random_beads.psf")["psf"]
        psf_hdf5_zo = numpy.load("sparse_random_hdf5_zo.psf")["psf"]
        psf_hdf5 = numpy.load("sparse_random_hdf5.psf")["psf"]

        diff_detected = diff_detected or psfDiffCheck(psf_beads, psf_hdf5_zo)
        diff_detected = diff_detected or psfDiffCheck(psf_beads, psf_hdf5)
    
    if diff_detected:
        print("Difference detected in PSF measurements!")
    else:
        print("No differences detected, all good.")

    if False:
        with tifffile.TiffWriter("psf_diff.tif") as tf:
            for i in range(psf_beads.shape[0]):
                tf.save((psf_beads[i,:,:] - psf_hdf5_zo[i,:,:]).astype(numpy.float32))


if (__name__ == "__main__"):
    measurePSF()
