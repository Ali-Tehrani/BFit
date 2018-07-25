# -*- coding: utf-8 -*-
# FittingBasisSets is a basis-set curve-fitting optimization package.
#
# Copyright (C) 2018 The FittingBasisSets Development Team.
#
# This file is part of FittingBasisSets.
#
# FittingBasisSets is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# FittingBasisSets is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# ---


import numpy as np
from numpy.testing import assert_almost_equal

from fitting.model import AtomicGaussianDensity, MolecularGaussianDensity
from fitting.fit import KLDivergenceSCF, GaussianBasisFit
from fitting.grid import UniformRadialGrid, CubicGrid


def test_lagrange_multiplier():
    g = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    e = np.exp(-g.points)
    kl = KLDivergenceSCF(g, e, None)
    assert_almost_equal(kl.lagrange_multiplier, 1., decimal=8)
    kl = KLDivergenceSCF(g, e, None, weights=2 * np.ones_like(e))
    assert_almost_equal(kl.lagrange_multiplier, 2., decimal=8)


def test_goodness_of_fit():
    g = UniformRadialGrid(1000, 0.0, 10.0, spherical=True)
    e = np.exp(-g.points)
    m = AtomicGaussianDensity(g.points, num_s=1, num_p=0, normalized=False)
    kl = KLDivergenceSCF(g, e, m, mask_value=0.)
    gf = kl.goodness_of_fit(np.array([1.]), np.array([1.]))
    expected = [5.56833, 4 * np.pi * 1.60909, 4. * np.pi * 17.360]
    assert_almost_equal(expected, gf, decimal=1)


def test_run_normalized_1s_gaussian():
    # density is normalized 1s orbital with exponent=1.0
    g = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    e = (1. / np.pi)**1.5 * np.exp(-g.points**2.)
    model = AtomicGaussianDensity(g.points, num_s=1, num_p=0, normalized=True)
    kl = KLDivergenceSCF(g, e, model, weights=None)

    # fit density with initial coeff=1. & expon=1.
    res = kl.run(np.array([1.]), np.array([1.]), True, True, 500, 1.e-4, 1.e-4, 1.e-4)
    # check optimized coeffs & expons
    assert_almost_equal(np.array([1.]), res["x"][0], decimal=8)
    assert_almost_equal(np.array([1.]), res["x"][1], decimal=8)
    # check value of optimized objective function & fitness measure
    assert_almost_equal(0., res["fun"][-1], decimal=10)
    assert_almost_equal(1., res["performance"][-1, 0], decimal=8)
    assert_almost_equal(0., res["performance"][-1, 1:], decimal=8)

    # fit density with initial coeff=0.5 & expon=0.5
    res = kl.run(np.array([0.5]), np.array([0.5]), True, True, 500, 1.e-4, 1.e-4, 1.e-4)
    # check optimized coeffs & expons
    assert_almost_equal(np.array([1.]), res["x"][0], decimal=8)
    assert_almost_equal(np.array([1.]), res["x"][1], decimal=8)
    # check value of optimized objective function & fitness measure
    assert_almost_equal(0., res["fun"][-1], decimal=10)
    assert_almost_equal(1., res["performance"][-1, 0], decimal=8)
    assert_almost_equal(0., res["performance"][-1, 1:], decimal=8)

    # fit density with initial coeff=0.1 & expon=10.
    res = kl.run(np.array([0.1]), np.array([10.]), True, True, 500, 1.e-4, 1.e-4, 1.e-4)
    # check optimized coeffs & expons
    assert_almost_equal(np.array([1.]), res["x"][0], decimal=8)
    assert_almost_equal(np.array([1.]), res["x"][1], decimal=8)
    # check value of optimized objective function
    assert_almost_equal(0., res["fun"][-1], decimal=10)

    # fit density with initial coeff=20. & expon=0.01.
    res = kl.run(np.array([20.]), np.array([0.01]), True, True, 500, 1.e-4, 1.e-4, 1.e-4)
    # check optimized coeffs & expons
    assert_almost_equal(np.array([1.]), res["x"][0], decimal=8)
    assert_almost_equal(np.array([1.]), res["x"][1], decimal=8)
    # check value of optimized objective function
    assert_almost_equal(0., res["fun"][-1], decimal=10)


def test_kl_scf_update_coeffs_2s_gaussian():
    # actual density is a 1s Slater function
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    cs, es = np.array([5., 2.]), np.array([10., 3.])
    dens = np.exp(-grid.points)
    # model density is a normalized 2s Gaussian basis
    model = AtomicGaussianDensity(grid.points, num_s=2, num_p=0, normalized=True)
    # test updating coeffs
    kl = KLDivergenceSCF(grid, dens, model)
    new_coeffs, new_expons = kl._update_params(cs, es, True, False)
    # compute model density
    approx = cs[0] * (es[0] / np.pi)**1.5 * np.exp(-es[0] * grid.points**2)
    approx += cs[1] * (es[1] / np.pi)**1.5 * np.exp(-es[1] * grid.points**2)
    # compute expected coeffs
    coeffs = cs * (es / np.pi)**1.5
    coeffs[0] *= grid.integrate(dens * np.exp(-es[0] * grid.points**2) / approx)
    coeffs[1] *= grid.integrate(dens * np.exp(-es[1] * grid.points**2) / approx)
    assert_almost_equal(new_expons, es, decimal=6)
    assert_almost_equal(new_coeffs, coeffs, decimal=6)


def test_kl_scf_update_params_2s_gaussian():
    # actual density is a 1s Slater function
    grid = UniformRadialGrid(1000, 0.0, 20.0, spherical=True)
    points = grid.points
    cs, es = np.array([5., 2.]), np.array([10., 3.])
    dens = np.exp(-points)
    # model density is a normalized 2s Gaussian basis
    model = AtomicGaussianDensity(points, num_s=2, num_p=0, normalized=True)
    # test updating coeffs
    kl = KLDivergenceSCF(grid, dens, model, mask_value=1.e-16)
    new_coeffs, new_expons = kl._update_params(cs, es, False, True)
    # compute model density
    approx = cs[0] * (es[0] / np.pi)**1.5 * np.exp(-es[0] * points**2)
    approx += cs[1] * (es[1] / np.pi)**1.5 * np.exp(-es[1] * points**2)
    # compute expected expons
    expons = 1.5 * np.ones(2)
    ratio = np.ma.filled(dens / np.ma.masked_less_equal(approx, 1.e-16), 1.)
    expons[0] *= grid.integrate(ratio * np.exp(-es[0] * points**2))
    expons[1] *= grid.integrate(ratio * np.exp(-es[1] * points**2))
    expons[0] /= grid.integrate(ratio * points**2 * np.exp(-es[0] * points**2))
    expons[1] /= grid.integrate(ratio * points**2 * np.exp(-es[1] * points**2))
    assert_almost_equal(new_coeffs, cs, decimal=6)
    assert_almost_equal(new_expons, expons, decimal=6)


def test_kl_scf_update_params_1s1p_gaussian():
    # actual density is a 1s Slater function
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs, es = np.array([1., 2.]), np.array([3., 4.])
    dens = np.exp(-grid.points)
    # model density is a normalized 2s Gaussian basis
    model = AtomicGaussianDensity(points, num_s=1, num_p=1, normalized=True)
    # compute model density
    approx = cs[0] * (es[0] / np.pi)**1.5 * np.exp(-es[0] * points**2)
    approx += cs[1] * 2. * es[1]**2.5 * points**2 * np.exp(-es[1] * points**2) / (3 * np.pi**1.5)
    # check model.evaluate
    assert_almost_equal(approx, model.evaluate(cs, es), decimal=6)
    # test updating coeffs
    kl = KLDivergenceSCF(grid, dens, model, mask_value=0.)
    new_coeffs, new_expons = kl._update_params(cs, es, update_coeffs=True, update_expons=False)
    coeffs = cs * np.array([(es[0] / np.pi)**1.5, 2 * es[1]**2.5 / (3 * np.pi**1.5)])
    coeffs[0] *= grid.integrate(dens * np.exp(-es[0] * points**2) / approx)
    coeffs[1] *= grid.integrate(dens * np.exp(-es[1] * points**2) * points**2 / approx)
    assert_almost_equal(new_expons, es, decimal=6)
    assert_almost_equal(new_coeffs, coeffs, decimal=6)
    # test updating expons
    new_coeffs, new_expons = kl._update_params(cs, es, update_coeffs=False, update_expons=True)
    expons = np.array([1.5, 2.5])
    expons[0] *= grid.integrate(dens * np.exp(-es[0] * points**2) / approx)
    expons[1] *= grid.integrate(dens * points**2 * np.exp(-es[1] * points**2) / approx)
    expons[0] /= grid.integrate(dens * points**2 * np.exp(-es[0] * points**2) / approx)
    expons[1] /= grid.integrate(dens * points**4 * np.exp(-es[1] * points**2) / approx)
    assert_almost_equal(new_coeffs, cs, decimal=6)
    assert_almost_equal(new_expons, expons, decimal=6)
    # test updating coeffs & expons
    new_coeffs, new_expons = kl._update_params(cs, es, update_coeffs=True, update_expons=True)
    assert_almost_equal(new_coeffs, coeffs, decimal=6)
    assert_almost_equal(new_expons, expons, decimal=6)


def test_kl_scf_update_params_3d_molecular_dens_1s_1s_gaussian():
    # actual density is a 1s Gaussian at origin
    grid = CubicGrid(-2., 2., 0.1)
    dens = np.exp(-np.sum(grid.points ** 2., axis=1))
    # model density is a normalized 1s Gassuain on each center
    coord = np.array([[0., 0., 0.], [0., 0., 1.]])
    cs, es = np.array([1., 2.]), np.array([3., 4.])
    model = MolecularGaussianDensity(grid.points, coord, np.array([[1, 0], [1, 0]]), True)
    kl = KLDivergenceSCF(grid, dens, model)
    # compute expected updated coeffs
    dist1 = np.sum((grid.points - coord[0])**2, axis=1)
    dist2 = np.sum((grid.points - coord[1])**2, axis=1)
    approx = cs[0] * (es[0] / np.pi)**1.5 * np.exp(-es[0] * dist1)
    approx += cs[1] * (es[1] / np.pi)**1.5 * np.exp(-es[1] * dist2)
    expected_coeffs = cs * (es / np.pi)**1.5
    expected_coeffs[0] *= grid.integrate(dens * np.exp(-es[0] * dist1) / approx)
    expected_coeffs[1] *= grid.integrate(dens * np.exp(-es[1] * dist2) / approx)
    # check updated coeffs
    coeffs, expons = kl._update_params(cs, es, update_coeffs=True, update_expons=False)
    assert_almost_equal(expons, es, decimal=6)
    assert_almost_equal(coeffs, expected_coeffs, decimal=6)
    # compute expected updated expons
    expected_expons = 1.5 * (es / np.pi)**1.5
    expected_expons[0] *= grid.integrate(dens * np.exp(-es[0] * dist1) / approx)
    expected_expons[1] *= grid.integrate(dens * np.exp(-es[1] * dist2) / approx)
    denoms = (es / np.pi)**1.5
    denoms[0] *= grid.integrate(dens * dist1 * np.exp(-es[0] * dist1) / approx)
    denoms[1] *= grid.integrate(dens * dist2 * np.exp(-es[1] * dist2) / approx)
    expected_expons /= denoms
    # check updated expons
    coeffs, expons = kl._update_params(cs, es, update_coeffs=False, update_expons=True)
    assert_almost_equal(coeffs, cs, decimal=6)
    assert_almost_equal(expons, expected_expons, decimal=6)


def test_kl_fit_unnormalized_dens_normalized_1s_gaussian():
    # density is normalized 1s orbital with exponent=1.0
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    # density is normalized 1s gaussian
    dens = 1.57 * np.exp(-0.51 * grid.points**2.)
    model = AtomicGaussianDensity(grid.points, num_s=1, num_p=0, normalized=True)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # expected coeffs & expons
    expected_cs = np.array([1.57 / (0.51 / np.pi)**1.5])
    expected_es = np.array([0.51])
    # initial coeff=1.57 & expon=0.51
    cs, es, f, df = kl.run(np.array([1.57]), np.array([0.51]), True, True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., 0.]), df, decimal=6)
    # initial coeff=0.1 & expon=0.1
    cs, es, f, df = kl.run(np.array([0.1]), np.array([0.1]), True, True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., 0.]), df, decimal=6)
    # initial coeff=5.0 & expon=15.
    cs, es, f, df = kl.run(np.array([5.0]), np.array([15.]), True, True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., 0.]), df, decimal=6)
    # initial coeff=0.8 & expon=0.51, opt coeffs
    cs, es, f, df = kl.run(np.array([0.5]), np.array([0.51]), True, False)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1.]), df, decimal=6)
    # # initial coeff=1.57 & expon=1., opt expons
    # cs, es, f, df = kl.run(np.array([1.57]), np.array([1.]), False, True)
    # assert_almost_equal(expected_cs, cs, decimal=8)
    # assert_almost_equal(expected_es, es, decimal=8)
    # assert_almost_equal(0., f, decimal=10)
    # assert_almost_equal(np.array([-1.]), df, decimal=6)


def test_kl_fit_normalized_dens_unnormalized_1s_gaussian():
    # density is normalized 1s gaussian
    grid = UniformRadialGrid(200, 0.0, 15.0, spherical=True)
    dens = 2.06 * (0.88 / np.pi)**1.5 * np.exp(-0.88 * grid.points**2.)
    # un-normalized 1s basis function
    model = AtomicGaussianDensity(grid.points, num_s=1, num_p=0, normalized=False)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # expected coeffs & expons
    expected_cs = np.array([2.06]) * (0.88 / np.pi)**1.5
    expected_es = np.array([0.88])
    # initial coeff=2.6 & expon=0.001
    cs, es, f, df = kl.run(np.array([2.6]), np.array([0.001]), opt_coeffs=True, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=7)
    assert_almost_equal(expected_es, es, decimal=7)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=1. & expon=0.88, opt coeffs
    cs, es, f, df = kl.run(np.array([1.0]), np.array([0.88]), opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1.]) / (0.88 / np.pi)**1.5, df, decimal=6)
    # initial coeff=10. & expon=0.88, opt coeffs
    cs, es, f, df = kl.run(np.array([10.]), np.array([0.88]), opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1.]) / (0.88 / np.pi)**1.5, df, decimal=6)
    # initial coeff=expected_cs & expon=expected_es, opt expons
    cs, es, f, df = kl.run(expected_cs, expected_es, opt_coeffs=False, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=expected_cs & expon=5.0, opt expons
    cs, es, f, df = kl.run(expected_cs, np.array([5.0]), opt_coeffs=False, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)


def test_kl_fit_normalized_dens_normalized_1s_gaussian():
    # density is normalized 1s gaussian
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    dens = 2.06 * (0.88 / np.pi)**1.5 * np.exp(-0.88 * grid.points**2.)
    # normalized 1s basis function
    model = AtomicGaussianDensity(grid.points, num_s=1, num_p=0, normalized=True)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # expected coeffs & expons
    expected_cs = np.array([2.06])
    expected_es = np.array([0.88])
    # initial coeff=2.6 & expon=0.001
    cs, es, f, df = kl.run(np.array([2.6]), np.array([0.001]), opt_coeffs=True, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., 0.]), df, decimal=6)
    # initial coeff=1. & expon=0.88, opt coeffs
    cs, es, f, df = kl.run(np.array([1.0]), np.array([0.88]), opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1.]), df, decimal=6)
    # initial coeff=10. & expon=0.88, opt coeffs
    cs, es, f, df = kl.run(np.array([10.]), np.array([0.88]), opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1.]), df, decimal=6)
    # initial coeff=expected_cs & expon=expected_es, opt expons
    cs, es, f, df = kl.run(expected_cs, expected_es, opt_coeffs=False, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=8)
    assert_almost_equal(expected_es, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([0.]), df, decimal=6)
    # initial coeff=expected_cs & expon=5.0, opt expons
    # cs, es, f, df = kl.run(expected_cs, np.array([5.0]), opt_coeffs=False, opt_expons=True)
    # assert_almost_equal(expected_cs, cs, decimal=8)
    # assert_almost_equal(expected_es, es, decimal=8)
    # assert_almost_equal(0., f, decimal=10)
    # assert_almost_equal(np.array([-1.]), df, decimal=6)


def test_kl_fit_normalized_dens_unnormalized_2p_gaussian():
    # density is normalized 2p orbitals
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs0 = np.array([0.76, 3.09])
    es0 = np.array([2.01, 0.83])
    dens = cs0[0] * es0[0]**2.5 * points**2 * np.exp(-es0[0] * points**2)
    dens += cs0[1] * es0[1]**2.5 * points**2 * np.exp(-es0[1] * points**2)
    dens *= 2. / (3. * np.pi**1.5)
    # un-normalized 2p functions
    model = AtomicGaussianDensity(points, num_s=0, num_p=2, normalized=False)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # expected coeffs & expons
    expected_cs = cs0 * es0**2.5 * 2. / (3. * np.pi**1.5)
    expected_es = es0
    # initial coeff=[1.5, 0.1] & expon=[4., 0.001]
    cs, es, f, df = kl.run(np.array([1.5, 0.1]), np.array([4.0, 0.001]), True, True)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(expected_es, es, decimal=5)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=cs0 & expon=es0, opt coeffs
    cs, es, f, df = kl.run(cs0, es0, opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(expected_es, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=[1.0, 1.0] & expon=es0, opt coeffs
    cs, es, f, df = kl.run(np.array([1.0, 1.0]), es0, opt_coeffs=True, opt_expons=False)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(expected_es, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=expected_cs & expon=[4.5, 1.0], opt expons
    cs, es, f, df = kl.run(expected_cs, np.array([4.5, 1.0]), opt_coeffs=False, opt_expons=True)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(expected_es, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)


def test_kl_fit_normalized_dens_normalized_2p_gaussian():
    # density is normalized 2p orbitals
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs0 = np.array([0.76, 3.09])
    es0 = np.array([2.01, 0.83])
    dens = cs0[0] * es0[0]**2.5 * points**2 * np.exp(-es0[0] * points**2)
    dens += cs0[1] * es0[1]**2.5 * points**2 * np.exp(-es0[1] * points**2)
    dens *= 2. / (3. * np.pi ** 1.5)
    # normalized 2p functions
    model = AtomicGaussianDensity(points, num_s=0, num_p=2, normalized=True)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # initial coeff=cs0 & expon=es0, opt coeffs
    cs, es, f, df = kl.run(cs0, es0, True, False)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1.]), df, decimal=6)
    # initial coeff=[2.5, 0.5] & expon=[2.0, 1.9]
    cs, es, f, df = kl.run(np.array([2.5, 0.5]), np.array([2.0, 1.9]), True, True)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=6)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=5)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1., 0., 0.]), df, decimal=6)
    # initial coeff=[1.0, 1.0] & expon=es0, opt coeffs
    cs, es, f, df = kl.run(np.array([1.0, 1.0]), es0, True, False)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1.]), df, decimal=6)
    # initial coeff=cs0 & expon=es0, opt coeffs
    cs, es, f, df = kl.run(cs0, es0, True, False)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1.]), df, decimal=6)
    # initial coeff=cs0 & expon=[2.0, 0.8]
    # cs, es, f, df = kl.run(cs0, np.array([2.0, 0.8]), False, True)


def test_kl_fit_normalized_dens_normalized_1s2p_gaussian():
    # density is normalized 1s + 2p gaussians
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs0 = np.array([1.52, 0.76, 3.09])
    es0 = np.array([0.50, 2.01, 0.83])
    dens = cs0[0] * (es0[0] / np.pi)**1.5 * np.exp(-es0[0] * points**2.)
    dens += cs0[1] * 2 * es0[1]**2.5 * points**2 * np.exp(-es0[1] * points**2) / (3. * np.pi**1.5)
    dens += cs0[2] * 2 * es0[2]**2.5 * points**2 * np.exp(-es0[2] * points**2) / (3. * np.pi**1.5)
    # un-normalized 1s + 2p functions
    model = AtomicGaussianDensity(points, num_s=1, num_p=2, normalized=True)
    kl = GaussianBasisFit(grid, dens, model, measure="kl", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.array([1., 1., 1.]), np.array([1., 1., 1.]), True, True)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=5)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=5)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1., -1., 0., 0., 0.]), df, decimal=6)
    # initial coeff=[0.1, 0.6, 7.] & expon=[1., 0.9, 1.0]
    cs, es, f, df = kl.run(np.array([0.1, 0.6, 7.]), np.array([1., 0.9, 1.0]), True, True)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=5)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=5)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1., -1., 0., 0., 0.]), df, decimal=6)
    # initial coeff=[1., 5., 0.] & expon=es0, opt coeffs
    cs, es, f, df = kl.run(np.array([1., 5., 0.]), es0, True, False)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=5)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=5)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([-1., -1., -1.]), df, decimal=6)
    # initial coeff=cs0 & expon=es0, opt expons
    cs, es, f, df = kl.run(cs0, es0, False, True)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=5)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=5)
    assert_almost_equal(0., f, decimal=10)
    assert_almost_equal(np.array([0., 0., 0.]), df, decimal=6)
    # # initial coeff=cs0 & expon=es0, opt expons
    # cs, es, f, df = kl.run(cs0, np.ones(3), False, True)
    # assert_almost_equal(np.array([cs0[1], cs0[0], cs0[2]]), cs, decimal=6)
    # assert_almost_equal(np.array([es0[1], es0[0], es0[2]]), es, decimal=6)
    # assert_almost_equal(0., f, decimal=10)
    # assert_almost_equal(np.array([0., 0., 0.]), df, decimal=6)


def test_kl_fit_unnormalized_1d_molecular_dens_unnormalized_1s_1s_gaussian():
    # density is normalized 1s + 1s gaussians
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs0 = np.array([1.52, 2.67])
    es0 = np.array([0.31, 0.41])
    coords = np.array([[0.], [1.]])
    # compute density on each center
    dens1 = cs0[0] * np.exp(-es0[0] * (points - coords[0])**2.)
    dens2 = cs0[1] * np.exp(-es0[1] * (points - coords[1])**2.)
    # un-normalized 1s + 1s functions
    model = MolecularGaussianDensity(points, coords, np.array([[1, 0], [1, 0]]), False)
    # fit total density
    kl = GaussianBasisFit(grid, dens1 + dens2, model, measure="kl", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(cs0, cs, decimal=4)
    assert_almost_equal(es0, es, decimal=4)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.array([5.45, 0.001]), es0, True, False)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(cs0, np.array([5.45, 0.001]), False, True)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 1
    kl = GaussianBasisFit(grid, dens1, model, measure="kl", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(np.array([cs[0], 0.]), cs, decimal=4)
    assert_almost_equal(es0[0], es[0], decimal=4)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.array([6.79, 8.51]), es0, True, False)
    assert_almost_equal(np.array([cs[0], 0.]), cs, decimal=4)
    assert_almost_equal(es0, es, decimal=4)
    assert_almost_equal(0., f, decimal=10)
    # initial coeff=1. & expon=1.
    cs, es, f, df = kl.run(np.array([1.52, 0.0]), np.array([3.0, 4.98]), False, True)
    assert_almost_equal(np.array([cs[0], 0.]), cs, decimal=4)
    assert_almost_equal(es0[0], es[0], decimal=4)
    assert_almost_equal(0., f, decimal=10)


def test_kl_fit_unnormalized_1d_molecular_dens_unnormalized_1s_1p_gaussian():
    # density is normalized 1s + 1s gaussians
    grid = UniformRadialGrid(150, 0.0, 15.0, spherical=True)
    points = grid.points
    cs0 = np.array([1.52, 2.67])
    es0 = np.array([0.31, 0.41])
    coords = np.array([[0.], [1.]])
    # compute density of each center
    dens_s = cs0[0] * (es0[0] / np.pi)**1.5 * np.exp(-es0[0] * (points - coords[0])**2.)
    dens_p = cs0[1] * (points - coords[1])**2 * np.exp(-es0[1] * (points - coords[1])**2.)
    dens_p *= (2. * es0[1]**2.5 / (3. * np.pi**1.5))
    # un-normalized 1s + 1p functions
    model = MolecularGaussianDensity(points, coords, np.array([[1, 0], [0, 1]]), True)
    # fit total density
    kl = GaussianBasisFit(grid, dens_s + dens_p, model, measure="kl", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = kl.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs, initial expon=es0
    cs, es, f, df = kl.run(np.array([5.91, 7.01]), es0, True, False)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. expons, initial coeff=cs0
    cs, es, f, df = kl.run(cs0, np.array([5.91, 7.01]), False, True)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 1
    kl = GaussianBasisFit(grid, dens_s, model, measure="kl", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = kl.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(np.array([cs0[0], 0.]), cs, decimal=6)
    assert_almost_equal(es0[0], es[0], decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # # fit 1p density on center 2
    kl = GaussianBasisFit(grid, dens_p, model, measure="kl", method="slsqp", mask_value=1.e-12)
    # opt. expons
    cs, es, f, df = kl.run(np.array([0., cs0[1]]), np.ones(2), False, True)
    assert_almost_equal(np.array([0., cs0[1]]), cs, decimal=6)
    assert_almost_equal(es0[1], es[1], decimal=6)
    assert_almost_equal(0., f, decimal=10)


def test_ls_fit_normalized_dens_normalized_1s_gaussian():
    # density is normalized 1s orbital with exponent=1.0
    grid = UniformRadialGrid(200, 0.0, 15.0, spherical=True)
    # actual density is a normalized 1s gaussian
    cs0, es0 = np.array([1.57]), np.array([0.51])
    dens = 1.57 * (0.51 / np.pi)**1.5 * np.exp(-0.51 * grid.points**2.)
    # model density is a normalized 1s Gaussian
    model = AtomicGaussianDensity(grid.points, num_s=1, num_p=0, normalized=True)
    ls = GaussianBasisFit(grid, dens, model, measure="sd", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = ls.run(np.array([0.1]), np.array([3.5]), True, True)
    assert_almost_equal(cs0, cs, decimal=8)
    assert_almost_equal(es0, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs
    cs, es, f, df = ls.run(np.array([10.]), np.array([0.51]), True, False)
    assert_almost_equal(cs0, cs, decimal=8)
    assert_almost_equal(es0, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)
    # model density is two normalized 1s Gaussian
    model = AtomicGaussianDensity(grid.points, num_s=2, num_p=0, normalized=True)
    ls = GaussianBasisFit(grid, dens, model, measure="sd", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = ls.run(np.array([0.1, 3.0]), np.array([5.1, 7.8]), True, True)
    assert_almost_equal(np.array([1.57, 0.]), cs, decimal=6)
    assert_almost_equal(np.array([0.51, 0.]), es, decimal=6)
    assert_almost_equal(0., f, decimal=10)


def test_ls_fit_normalized_dens_normalized_2s_gaussian():
    # density is normalized 1s orbital with exponent=1.0
    grid = UniformRadialGrid(300, 0.0, 15.0, spherical=True)
    # actual density is a normalized 1s gaussian
    cs0 = np.array([1.57, 0.12])
    es0 = np.array([0.45, 1.29])
    # evaluate normalized 8s density
    dens = cs0[0] * (es0[0] / np.pi)**1.5 * np.exp(-es0[0] * grid.points**2.)
    dens += cs0[1] * (es0[1] / np.pi)**1.5 * np.exp(-es0[1] * grid.points**2.)
    # check norm of density
    assert_almost_equal(grid.integrate(dens), np.sum(cs0), decimal=6)
    # model density is a normalized 2s Gaussian
    model = AtomicGaussianDensity(grid.points, num_s=2, num_p=0, normalized=True)
    ls = GaussianBasisFit(grid, dens, model, measure="sd", method="slsqp")
    initial_cs = np.array([0.57, 0.98])
    initial_es = np.array([1.67, 0.39])
    # opt. coeffs & expons
    cs, es, f, df = ls.run(initial_cs, initial_es, True, True)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=6)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs
    cs, es, f, df = ls.run(initial_cs, es0, True, False)
    assert_almost_equal(cs0, cs, decimal=8)
    assert_almost_equal(es0, es, decimal=8)
    assert_almost_equal(0., f, decimal=10)


def test_ls_fit_normalized_dens_normalized_5s_gaussian():
    # density is normalized 1s orbital with exponent=1.0
    grid = UniformRadialGrid(300, 0.0, 15.0, spherical=True)
    # actual density is a normalized 5s gaussian
    cs0 = np.array([1.57, 0.12, 3.67, 0.97, 5.05])
    es0 = np.array([0.45, 1.29, 1.25, 20.1, 10.5])
    # evaluate normalized 5s density
    dens = cs0[0] * (es0[0] / np.pi)**1.5 * np.exp(-es0[0] * grid.points**2)
    dens += cs0[1] * (es0[1] / np.pi)**1.5 * np.exp(-es0[1] * grid.points**2)
    dens += cs0[2] * (es0[2] / np.pi)**1.5 * np.exp(-es0[2] * grid.points**2)
    dens += cs0[3] * (es0[3] / np.pi)**1.5 * np.exp(-es0[3] * grid.points**2)
    dens += cs0[4] * (es0[4] / np.pi)**1.5 * np.exp(-es0[4] * grid.points**2)
    # check norm of density
    assert_almost_equal(grid.integrate(dens), np.sum(cs0), decimal=6)
    # model density is a normalized 1s Gaussian
    model = AtomicGaussianDensity(grid.points, num_s=5, num_p=0, normalized=True)
    ls = GaussianBasisFit(grid, dens, model, measure="sd", method="slsqp")
    initial_cs = np.array([0.57, 0.98, 1.16, 9.26, 2.48])
    initial_es = np.array([1.67, 0.39, 1.79, 13.58, 18.69])
    # opt. coeffs & expons
    cs, es, f, df = ls.run(initial_cs, initial_es, True, True)
    # assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=6)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=1)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs
    cs, es, f, df = ls.run(initial_cs, es0, True, False)
    assert_almost_equal(np.sort(cs0), np.sort(cs), decimal=6)
    assert_almost_equal(np.sort(es0), np.sort(es), decimal=6)
    assert_almost_equal(0., f, decimal=10)


def test_ls_fit_unnormalized_1d_molecular_dens_unnormalized_1s_1s_gaussian():
    # density is normalized 1s + 1s gaussians
    grid = UniformRadialGrid(200, 0.0, 15.0, spherical=True)
    cs0, es0 = np.array([1.52, 2.67, ]), np.array([0.31, 0.41])
    coords = np.array([[0.], [1.]])
    # compute density on each center
    dens1 = cs0[0] * np.exp(-es0[0] * (grid.points - coords[0])**2.)
    dens2 = cs0[1] * np.exp(-es0[1] * (grid.points - coords[1])**2.)
    # un-normalized 1s + 1s basis functions
    model = MolecularGaussianDensity(grid.points, coords, np.array([[1, 0], [1, 0]]), False)
    # fit total density
    ls = GaussianBasisFit(grid, dens1 + dens2, model, measure="sd", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = ls.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(cs0, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 1
    ls = GaussianBasisFit(grid, dens1, model, measure="sd", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = ls.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(np.array([1.52, 0.0]), cs, decimal=6)
    assert_almost_equal(es0[0], es[0], decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 2
    ls = GaussianBasisFit(grid, dens2, model, measure="sd", method="slsqp")
    # initial coeff=1. & expon=1.
    cs, es, f, df = ls.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(np.array([0.0, 2.67]), cs, decimal=6)
    assert_almost_equal(es0[1], es[1], decimal=6)
    assert_almost_equal(0., f, decimal=10)


def test_ls_fit_normalized_1d_molecular_dens_unnormalized_1s_1p_gaussian():
    # density is normalized 1s + 1s gaussians
    grid = UniformRadialGrid(200, 0.0, 15.0, spherical=True)
    cs0, es0 = np.array([1.52, 2.67]), np.array([0.31, 0.41])
    coords = np.array([[0.0], [1.0]])
    # compute density of each center
    dens_s = cs0[0] * (es0[0] / np.pi)**1.5 * np.exp(-es0[0] * (grid.points - coords[0])**2.)
    dens_p = cs0[1] * (grid.points - coords[1])**2 * np.exp(-es0[1] * (grid.points - coords[1])**2)
    dens_p *= (2. * es0[1]**2.5 / (3. * np.pi**1.5))
    # normalized 1s + 1p basis functions
    model = MolecularGaussianDensity(grid.points, coords, np.array([[1, 0], [0, 1]]), False)
    expected_cs = cs0 * np.array([(es0[0] / np.pi)**1.5, 2. * es0[1]**2.5 / (3. * np.pi**1.5)])
    # fit total density
    ls = GaussianBasisFit(grid, dens_s + dens_p, model, measure="sd", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = ls.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs
    cs, es, f, df = ls.run(np.array([0.001, 3.671]), es0, True, False)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. expons
    cs, es, f, df = ls.run(expected_cs, np.array([2.5, 1.9]), False, True)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 1
    ls = GaussianBasisFit(grid, dens_s, model, measure="sd", method="slsqp")
    # opt. coeffs & expons
    cs, es, f, df = ls.run(np.ones(2), np.ones(2), True, True)
    assert_almost_equal(np.array([expected_cs[0], 0.]), cs, decimal=6)
    assert_almost_equal(es0[0], es[0], decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # opt. coeffs
    cs, es, f, df = ls.run(np.array([0.05, 5.01]), es0, True, False)
    assert_almost_equal(np.array([expected_cs[0], 0.]), cs, decimal=6)
    assert_almost_equal(es0, es, decimal=6)
    assert_almost_equal(0., f, decimal=10)
    # fit 1s density on center 1
    ls = GaussianBasisFit(grid, dens_p, model, measure="sd", method="slsqp")
    # opt. expons
    cs, es, f, df = ls.run(expected_cs, np.array([2.5, 1.9]), False, True)
    assert_almost_equal(expected_cs, cs, decimal=6)
    assert_almost_equal(es0[1], es[1], decimal=6)
    assert_almost_equal(0., f, decimal=10)
