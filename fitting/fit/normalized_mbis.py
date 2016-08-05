from fitting.fit.model import *
from fitting.fit.GaussianBasisSet import *
from fitting.fit.multi_objective import GaussianSecondObjTrapz, GaussianSecondObjSquared
import  matplotlib.pyplot as plt
from scipy.integrate import simps, trapz

import numpy as np

def get_normalization_constant(exponent):
    #return (exponent / np.pi)**(3/2)
    return  4 * exponent**(3/2) / np.pi**(1/2)

def get_normalization_constant2(exponent):
    return (exponent / np.pi )**(1/2) * 2.

def normalized_gaussian_model(coefficients, exponents, grid):
    exponential = np.exp(-exponents * np.power(grid, 2.))
    normalization_constants = np.array([get_normalization_constant(exponents[x])  for x in range(0, len(exponents))])
    normalized_coeffs = normalization_constants * coefficients
    gaussian_density = np.dot(exponential, normalized_coeffs)
    return gaussian_density

def get_gaussian_model(coefficients, exponents, grid):
    exponential = np.exp(-exponents * np.power(grid, 2.))
    gaussian_density = np.dot(exponential, coefficients)
    return gaussian_density

def integrate_error(coefficients, exponents, electron_density, grid):
    gaussian_model = normalized_gaussian_model(coefficients, exponents, grid)
    return np.trapz(y=np.ravel(np.power(grid, 2.)) * np.abs(gaussian_model - np.ravel(electron_density)) ,x=
            np.ravel(grid))

def integrate_normalized_model(coefficients, exponents, electron_density, grid):
    gaussian_model = normalized_gaussian_model(coefficients, exponents, grid)
    return np.trapz(y=np.power(np.ravel(grid), 2.) * gaussian_model , x=np.ravel(grid))

def KL_objective_function(coefficients, exponents, true_density, grid):
    gaussian_density = normalized_gaussian_model(coefficients, exponents, grid)
    masked_gaussian_density = np.ma.asarray(gaussian_density)
    masked_electron_density = np.ma.asarray(np.ravel(true_density))
    #masked_gaussian_density[masked_gaussian_density <= 1e-6] = 1e-12

    ratio = masked_electron_density / masked_gaussian_density
    return np.trapz(y=masked_electron_density * np.log(ratio), x=np.ravel(grid))


def update_coefficients(initial_coeffs, constant_exponents, electron_density, grid, masked_value=1e-6):
    assert np.all(initial_coeffs > 0) == True, "Coefficinets should be positive non zero, " + str(initial_coeffs)
    assert len(initial_coeffs) == len(constant_exponents)
    assert len(np.ravel(electron_density)) == len(np.ravel(grid))

    gaussian_density = normalized_gaussian_model(initial_coeffs, constant_exponents,  grid)

    masked_gaussian_density = np.ma.asarray(gaussian_density)
    masked_electron_density = np.ma.asarray(np.ravel(electron_density))
    masked_gaussian_density[masked_gaussian_density <= masked_value] = masked_value

    ratio = masked_electron_density / masked_gaussian_density

    new_coefficients = np.empty(len(initial_coeffs))
    for i in range(0, len(initial_coeffs)):
        factor = initial_coeffs[i] * get_normalization_constant(constant_exponents[i])
        integrand = ratio * np.ravel(np.ma.asarray(np.exp(- constant_exponents[i] * np.power(grid, 2.)))) *\
                    np.ravel(np.power(grid, 2.))
        new_coefficients[i] = factor * np.trapz(y=integrand, x=np.ravel(grid))
    print(np.sum(new_coefficients))
    return new_coefficients

def update_exponents(constant_coeffs, initial_exponents, electron_density, grid, masked_value=1e-6):
    gaussian_density = normalized_gaussian_model(constant_coeffs, initial_exponents, grid)

    masked_gaussian_density = np.ma.asarray(gaussian_density)
    masked_electron_density = np.ma.asarray(np.ravel(electron_density))
    masked_gaussian_density[masked_gaussian_density <= masked_value] = masked_value

    ratio = masked_electron_density / masked_gaussian_density
    new_exponents = np.empty(len(initial_exponents))
    masked_grid = np.ma.asarray(np.ravel(grid))
    masked_grid_squared = np.ma.asarray(np.ravel(np.power(grid, 4.)))

    for i in range(0, len(initial_exponents)):
        factor = 2. * get_normalization_constant(initial_exponents[i])
        integrand = ratio * np.ravel(np.ma.asarray(np.exp(- initial_exponents[i] * np.power(grid, 2.)))) *\
                    masked_grid_squared
        denom = (factor * np.trapz(y=integrand, x=masked_grid))
        new_exponents[i] = 3. / denom
    return new_exponents

def fixed_iteration_MBIS_method(coefficients, exponents,  electron_density, grid, num_of_iterations=800,masked_value=1e-6, iprint=False):
    current_error = 1e10
    old_coefficients = np.copy(coefficients)
    new_coefficients = np.copy(coefficients)
    counter = 0
    error_array = [ [], [], [], [], [] ,[]]

    for x in range(0, num_of_iterations):
        temp_coefficients = new_coefficients.copy()

        new_coefficients = update_coefficients(old_coefficients, exponents,electron_density,
                                               grid, masked_value=masked_value)
        #exponents = update_exponents(old_coefficients, exponents, electron_density, grid)
        old_coefficients = temp_coefficients.copy()

        approx_model = normalized_gaussian_model(new_coefficients, exponents, grid)
        inte_error = integrate_error(new_coefficients, exponents, electron_density, grid)
        integration_model = integrate_normalized_model(new_coefficients, exponents, electron_density, grid)
        obj_func_error = KL_objective_function(new_coefficients, exponents, electron_density, grid)
        if x % 1000 == 0.:
            print("Coeffs")
            print(new_coefficients)
            print("Exps")
            print(exponents)
        if iprint:
            print(counter, integration_model,
               inte_error,
               obj_func_error)

        error_array[0].append(inte_error)
        error_array[1].append(integration_model)
        error_array[2].append(obj_func_error)
        counter += 1
    return((coeffs, exps), error_array)

if __name__ == "__main__":
    ELEMENT_NAME = "be"
    ATOMIC_NUMBER = 4
    file_path = r"C:\Users\Alireza\PycharmProjects\fitting\fitting\data\examples\\" + ELEMENT_NAME + ".slater"
    #Create Grid for the modeling
    from fitting.density.radial_grid import *
    radial_grid = Radial_Grid(ATOMIC_NUMBER)
    NUMBER_OF_CORE_POINTS = 300; NUMBER_OF_DIFFUSED_PTS = 400
    row_grid_points = radial_grid.grid_points(NUMBER_OF_CORE_POINTS, NUMBER_OF_DIFFUSED_PTS, [50, 75, 100])
    column_grid_points = np.reshape(row_grid_points, (len(row_grid_points), 1))

    be =  GaussianTotalBasisSet(ELEMENT_NAME, column_grid_points, file_path)
    fitting_obj = Fitting(be)

    exps = np.array([  2.50000000e-02,   5.00000000e-02,   1.00000000e-01,   2.00000000e-01,
                   4.00000000e-01,   8.00000000e-01,   1.60000000e+00,   3.20000000e+00,
                   6.40000000e+00,   1.28000000e+01,   2.56000000e+01,   5.12000000e+01,
                   1.02400000e+02,   2.04800000e+02,   4.09600000e+02,   8.19200000e+02,
                   1.63840000e+03,   3.27680000e+03,   6.55360000e+03,   1.31072000e+04,
                   2.62144000e+04,   5.24288000e+04,   1.04857600e+05,   2.09715200e+05,
                   4.19430400e+05,   8.38860800e+05,   1.67772160e+06,   3.35544320e+06,
                   6.71088640e+06,   1.34217728e+07,   2.68435456e+07,   5.36870912e+07,
                   1.07374182e+08,   2.14748365e+08,   4.29496730e+08,   8.58993459e+08,
                   1.71798692e+09,   3.43597384e+09])
    exps = be.UGBS_s_exponents
    coeffs = fitting_obj.optimize_using_nnls(be.create_cofactor_matrix(exps))
    coeffs[coeffs == 0.] = 1e-12


    #print("paams", parameters)
    #model = be.create_model(np.append(parameters,exps), len(parameters))
    #print(be.integrate_model_using_trapz(model))
    fixed_iteration_MBIS_method(coeffs, exps, be.electron_density, be.grid, num_of_iterations=10000000,iprint=True)

