#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The array_analysis test suite.
"""

import unittest
import numpy as np
from obspy.signal.array_analysis import array_rotation_strain

class ArrayTestCase(unittest.TestCase):
    """
    Test cases for array_analysis functions.
    """
    def setUp(self):
        self.array_coords = np.array([[   0.0,    0.0,   0.0],
                                               [  -5.0,    7.0,   0.0],
                                               [   5.0,    7.0,   0.0],
                                               [  10.0,    0.0,   0.0],
                                               [   5.0,   -7.0,   0.0],
                                               [  -5.0,   -7.0,   0.0],
                                               [ -10.0,    0.0,   0.0]])
        self.subarray = np.array([0, 1, 2, 3, 4, 5, 6])
        self.ts1 = np.empty((1000, 7)) * np.NaN
        self.ts2 = np.empty((1000, 7)) * np.NaN
        self.ts3 = np.empty((1000, 7)) * np.NaN
        self.sigmau = 0.0001
        self.Vp = 1.93  
        self.Vs = 0.326 

    def tearDown(self):
        pass
    
    def test_array_rotation(self):
        # tests function array_rotation_strain with synthetic data with pure
        # rotation and no strain
        array_coords = self.array_coords        
        subarray = self.subarray
        ts1 = self.ts1
        ts2 = self.ts2
        ts3 = self.ts3
        sigmau = self.sigmau
        Vp = self.Vp
        Vs = self.Vs

        rotx = 0.00001 * np.exp(-1*np.square(np.linspace(-2, 2, 1000))) * \
                np.sin(np.linspace(-30*np.pi, 30*np.pi, 1000))
        roty = 0.00001 * np.exp(-1*np.square(np.linspace(-2, 2, 1000))) * \
                np.sin(np.linspace(-20*np.pi, 20*np.pi, 1000))
        rotz = 0.00001 * np.exp(-1*np.square(np.linspace(-2, 2, 1000))) * \
                np.sin(np.linspace(-10*np.pi, 10*np.pi, 1000))

        for stat in xrange(7):
            for t in xrange(1000):
                ts1[t, stat] = -1. * array_coords[stat, 1] * rotz[t]
                ts2[t, stat] = array_coords[stat, 0] * rotz[t]
                ts3[t, stat] = array_coords[stat, 1] * rotx[t] - \
                        array_coords[stat, 0] * roty[t] 

        out = array_rotation_strain(subarray, ts1, ts2, ts3, Vp, Vs,
                                    array_coords, sigmau)

        np.testing.assert_array_almost_equal(rotx, out['ts_w1'], decimal=12)
        np.testing.assert_array_almost_equal(roty, out['ts_w2'], decimal=12)
        np.testing.assert_array_almost_equal(rotz, out['ts_w3'], decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_s'],
                decimal=15)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_d'],
                decimal=15)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_M'],
                decimal=12)


    def test_array_dilation(self):
        # tests function array_rotation_strain with synthetic data with pure
        # dilation and no rotation or shear strain
        array_coords = self.array_coords        
        subarray = self.subarray
        ts1 = self.ts1
        ts2 = self.ts2
        ts3 = self.ts3
        sigmau = self.sigmau
        Vp = self.Vp
        Vs = self.Vs
        
        eta = 1 - 2*Vs**2/Vp**2

        dilation = .00001 * np.exp(-1*np.square(np.linspace(-2, 2, 1000))) * \
                np.sin(np.linspace(-40*np.pi, 40*np.pi, 1000))

        for stat in xrange(7):
            for t in xrange(1000):
                ts1[t, stat] = array_coords[stat, 0] * dilation[t]
                ts2[t, stat] = array_coords[stat, 1] * dilation[t]
                ts3[t, stat] = array_coords[stat, 2] * dilation[t]

        out = array_rotation_strain(subarray, ts1, ts2, ts3, Vp, Vs,
                                    array_coords, sigmau)

        # remember free surface boundary conditions!
        # see Spudich et al, 1995, (A2)
        np.testing.assert_array_almost_equal(dilation * (2-2*eta),
                out['ts_d'], decimal=12)
        np.testing.assert_array_almost_equal(dilation * 2 , out['ts_dh'],
                decimal=12)
        np.testing.assert_array_almost_equal(abs(dilation * .5 * (1 + \
                2*eta)), out['ts_s'], decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_sh'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w1'],
                decimal=15)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w2'],
                decimal=15)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w3'],
                decimal=15)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_M'],
                decimal=12)


    def test_array_horizontal_shear(self):
        # tests function array_rotation_strain with synthetic data with pure
        # horizontal shear strain, no rotation or dilation
        array_coords = self.array_coords        
        subarray = self.subarray
        ts1 = self.ts1
        ts2 = self.ts2
        ts3 = self.ts3
        sigmau = self.sigmau
        Vp = self.Vp
        Vs = self.Vs
        
        shear_strainh= .00001 * np.exp(-1*np.square(np.linspace(-2, 2, 1000)))\
                * np.sin(np.linspace(-10*np.pi, 10*np.pi, 1000))

        ts3 = np.zeros((1000, 7))

        for stat in xrange(7):
            for t in xrange(1000):
                ts1[t, stat] = array_coords[stat, 1] * shear_strainh[t]
                ts2[t, stat] = array_coords[stat, 0] * shear_strainh[t]

        out = array_rotation_strain(subarray, ts1, ts2, ts3, Vp, Vs,
                                    array_coords, sigmau)

        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_d'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_dh'],
                decimal=12)
        np.testing.assert_array_almost_equal(abs(shear_strainh), out['ts_s'],
                decimal=12)
        np.testing.assert_array_almost_equal(abs(shear_strainh), out['ts_sh'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w1'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w2'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_w3'],
                decimal=12)
        np.testing.assert_array_almost_equal(np.zeros(1000), out['ts_M'],
                decimal=12)

def suite():
    return unittest.makeSuite(ArrayTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
