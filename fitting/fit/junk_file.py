import numpy as np
from fitting.fit.model import *
from fitting.fit.GaussianBasisSet import *
from fitting.fit.MBIS import KL_objective_function
from scipy.optimize import broyden2

def get_exponents(electron_density, grid, atomic_number, coeff):
    return -(np.trapz(y=np.ravel(electron_density) * np.log(np.ravel(electron_density) / coeff), x=np.ravel(grid))) / atomic_number


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

    print("log", np.log(300 / 1e-3))
    coeffs = np.array([  1.41767301e-02,   1.61217003e-02,   5.37670085e-03,   4.48433204e-01,
       1.43127076e-12,   1.41168153e-12,   1.10299014e-12,   3.05620079e+00,
       2.77566789e+01,   5.26867277e+01,   7.26195260e+01,   6.67535238e+01,
       5.90642139e+01,   4.21070056e+01,   3.54297906e+01,   2.50726023e+01,
       1.69935475e+01,   1.22501713e+01,   9.13462021e+00,   6.10369988e+00,
       4.47340624e+00,   3.06963150e+00,   2.27888360e+00,   1.50223651e+00,
       1.11518137e+00,   7.34576917e-01,   5.25742887e-01,   3.13040994e-01,
       1.81798146e-01,   1.37329668e-01,   7.41491243e-02,   7.12766917e-02,
       3.72533982e-05,   8.09492657e-05,   4.71732744e-05,   1.98518608e-12,
       3.98479641e-11,   6.83986285e+01])

    exps = np.array([  1.03455184e-01,   1.03455184e-01,   1.03455184e-01,   2.44326240e-01,
       2.44516309e-01,   2.44516309e-01,   2.44516340e-01,   4.06344772e+00,
       5.98665066e+00,   1.31392429e+01,   2.42795613e+01,   5.22404524e+01,
       1.02655614e+02,   1.55440691e+02,   5.49308608e+02,   5.82229234e+02,
       1.35810193e+03,   3.88515080e+03,   5.64875569e+03,   1.07580370e+04,
       2.67246131e+04,   5.17844800e+04,   9.16580170e+04,   1.83110927e+05,
       4.14135488e+05,   7.10749249e+05,   1.19055731e+06,   1.79857559e+06,
       7.77001030e+06,   7.87089371e+06,   7.91209874e+06,   7.96024810e+06,
       2.37506233e+08,   2.37506353e+08,   2.83741684e+10,   2.83741684e+10,
       2.83741684e+10,   2.83741684e+10])
    model = be.create_model(np.append(coeffs,exps), len(exps))
    be.plot_atomic_density(be.grid, [(model, "model"), (be.electron_density, "True")], "Plotted Density", "PlottedDens")