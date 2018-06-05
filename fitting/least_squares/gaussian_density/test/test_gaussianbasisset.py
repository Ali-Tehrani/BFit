# -*- coding: utf-8 -*-
# An basis-set curve-fitting optimization package.
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
r"""Test file for 'fitting.least_squares.gaussian_density.total_Gaussian_dens."""

import numpy as np
import numpy.testing as npt
import scipy.optimize
from fitting.least_squares.gaussian_density.gaussian_dens import GaussianBasisSet

__all__ = [
    "test_cost_function",
    "test_create_model",
    "test_derivative_coefficient",
    "test_derivative_cost_function",
    "test_derivative_exponents",
    "test_input",
    "test_residual"
]


def test_input():
    r"""Test inputs for gaussian basis set class."""
    g = np.array([50., 50.])
    npt.assert_raises(TypeError, GaussianBasisSet, 10, g)
    npt.assert_raises(TypeError, GaussianBasisSet, g, 10.)


def gaussian_func(c, exps, grid):
    return [np.sum([c[i] * np.exp(-exps[i] * j**2.) for i in range(0, len(exps))])
            for j in grid]


def test_create_model():
    r"""Test create_model in GaussianBasisSet class."""
    # Test one point only
    exponent = 2.0
    coeff = 3.
    exponential = coeff * np.exp(-1 * exponent * 1.0**2)
    # One Coefficient (3.) and one exponent( 2.)
    parameters = np.array([coeff, exponent])
    grid = np.array([1.0])
    true_model = np.exp(-grid)

    model_object = GaussianBasisSet(grid, true_model)
    model = model_object.create_model(parameters)
    assert np.abs(exponential - model) < 1e-13

    # Multiple Value Test with multiple coefficients and exponents.
    grid = np.arange(1, 6)
    true_model = np.exp(-grid)
    model_object = GaussianBasisSet(grid, true_model)
    parameters = np.array([2, 2, 2, 4, 5, 1, 2, 3, 4, 5])
    model = model_object.create_model(parameters)
    actual_answer = gaussian_func(parameters[:len(parameters)//2],
                                  parameters[len(parameters)//2:],
                                  grid)
    assert np.abs(model[0] - actual_answer[0]) < 1e-5
    assert model[1] == actual_answer[1]
    assert model[2] == actual_answer[2]

    # Test for which_opti == c, ie optimizing coefficients.
    parameters = np.array([2, 2, 2, 4, 5])
    fixed_params = np.array([1, 2, 3, 4, 5])
    model = model_object.create_model(parameters, fixed_params, which_opti="c")
    actual_answer = gaussian_func(parameters, fixed_params, grid)
    assert np.abs(model[0] - actual_answer[0]) < 1e-5
    assert model[1] == actual_answer[1]
    assert model[2] == actual_answer[2]

    # Test which_opti == e
    parameters = np.array([1, 2, 3, 4, 5])
    fixed_params = np.array([2, 2, 2, 4, 5])
    model = model_object.create_model(parameters, fixed_params, which_opti="e")
    actual_answer = gaussian_func(fixed_params, parameters, grid)
    assert np.abs(model[0] - actual_answer[0]) < 1e-5
    assert model[1] == actual_answer[1]
    assert model[2] == actual_answer[2]


def test_cost_function():
    r"""Test cost_function in GaussianBasisSet class."""
    # Test at one point wrt to slater density
    grid = 3.0
    coeff = 4.0
    exponent = 5.0
    model = coeff * np.exp(-exponent * grid**2)

    parameters = np.array([coeff, exponent])
    grid = np.array([3.0])
    true_model = np.exp(-grid)

    model_object = GaussianBasisSet(grid, true_model)
    electron_density = model_object.true_model
    desired_answer = (electron_density - model)**2
    actual_answer = model_object.cost_function(parameters, 1)
    npt.assert_allclose(actual_answer, desired_answer)

    # Test with multiply points
    grid = np.arange(1., 3.)
    true_model = np.exp(-grid)
    model_object = GaussianBasisSet(grid, true_model)
    parameters = np.array([1.0, 2.0, 3.0, 4.0])
    actual_answer = model_object.cost_function(parameters)
    calc_value = np.array([1.0 * np.exp(-3.0 * 1.0**2) + 2.0 * np.exp(-4.0 * 1.0**2),
                           1.0 * np.exp(-3.0 * 2.0**2) + 2.0 * np.exp(-4.0 * 2.0**2)])
    desired_answer = (model_object.true_model - calc_value)**2.
    npt.assert_allclose(np.sum(desired_answer), actual_answer)


def test_residual():
    r"""Test residual function for GaussianBasisSet."""
    grid = np.array([1., 2.])
    true_model = np.exp(-grid)
    obj = GaussianBasisSet(grid, true_model)
    parameters = np.array([1., 2., 3., 4.])
    actual_answer = obj.get_residual(parameters)
    a = np.exp(-3) + 2. * np.exp(-4)
    b = np.exp(-3 * 2**2) + 2. * np.exp(-4. * 2**2)
    desired_answer = [obj.true_model[0] - a,
                      obj.true_model[1] - b]
    npt.assert_allclose(actual_answer, desired_answer)

    grid = np.array([1., 2.], dtype=np.double)
    true_model = np.exp(-grid, true_model)
    p = np.array([1., 2., 3., 4.], dtype=np.double)
    obj = GaussianBasisSet(grid, true_model)
    actual_answer = obj.get_residual(p)

    den = obj.true_model.copy()
    c = (den - gaussian_func([1., 2.], [3., 4.], grid))
    npt.assert_almost_equal(actual_answer[0], c[0])
    npt.assert_almost_equal(actual_answer[1], c[1])


def test_derivative_coefficient():
    r"""Test derivative with respect to coefficients."""
    grid = np.array([1., 2.], dtype=np.double)
    exps = np.array([3., 4.])
    true_dens = np.exp(-grid)
    obj = GaussianBasisSet(grid, true_dens)
    dens = obj.true_model

    residual = 2. * np.array([dens[0] - np.exp(-3) - 2. * np.exp(-4),
                              dens[1] - np.exp(-12) - 2. * np.exp(-16)])
    actual_answer = obj._deriv_wrt_coeffs(exps, residual)
    desired_answer = [residual[0] * -np.exp(-3) + residual[1] * -np.exp(-12),
                      residual[0] * -np.exp(-4) + residual[1] * -np.exp(-16)]
    npt.assert_allclose(actual_answer, desired_answer, rtol=1e-3)


def test_derivative_exponents():
    r"""Test derivative with respect to exponents."""
    grid = np.array([1., 2.], dtype=np.double)
    coeff = np.array([1., 2.])
    exps = np.array([3., 4.])
    den = np.exp(-grid)
    obj = GaussianBasisSet(grid, den)
    actual_answer = obj.derivative_of_cost_function(exps, coeff, which_opti='e')

    c = 2. * (den - gaussian_func([1., 2.], [3., 4.], grid))
    deriv_e1 = c[0] * coeff[0] * np.exp(-exps[0]) + \
        c[1] * coeff[0] * 4 * np.exp(-exps[0] * 4)
    deriv_e2 = c[0] * coeff[1] * np.exp(-exps[1]) + \
        c[1] * coeff[1] * 4 * np.exp(-exps[1] * 4)
    npt.assert_allclose(actual_answer, [np.sum(deriv_e1), np.sum(deriv_e2)])


def test_derivative_cost_function():
    r"""Test derivaitve of cost function for GaussianBasisSet."""
    # Test With Array WRT TO ONLY COEFFICIENT
    grid = np.array([1., 2.], dtype=np.double)
    coeff = np.array([1., 2.])
    exps = np.array([3., 4.])
    den = np.exp(-grid)
    obj = GaussianBasisSet(grid, den)
    actual_answer = obj.derivative_of_cost_function(coeff, exps, which_opti='c')

    c = -2. * (den - gaussian_func([1., 2.], [3., 4.], grid))
    npt.assert_almost_equal(c[0], -2 * (den[0] - np.exp(-3) - 2. * np.exp(-4)))
    npt.assert_almost_equal(c[1], -2 * (den[1] - np.exp(-12) - 2. * np.exp(-16)))

    deriv_c = c * np.exp(-exps[0] * grid**2.)
    deriv_c2 = c * np.exp(-exps[1] * grid**2.)
    npt.assert_allclose(actual_answer, [np.sum(deriv_c), np.sum(deriv_c2)])

    # Test with Scipy
    grid = np.array([5.0])
    exponents = np.array([0., 1., 2., 3., 4.])
    coefficient = np.array([5.0, 3.0, 2.0, 2.44, 5.6])
    den = np.exp(-grid)
    parameters = np.append(coefficient, exponents)
    model_object = GaussianBasisSet(grid, den)
    approximation = scipy.optimize.approx_fprime(parameters,
                                                 model_object.cost_function,
                                                 1e-5, 5)
    derivative = model_object.derivative_of_cost_function(parameters)
    npt.assert_allclose(approximation, derivative, rtol=1e-3, atol=1e-1)
