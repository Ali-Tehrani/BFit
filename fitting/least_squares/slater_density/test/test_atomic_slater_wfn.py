r"""Test file for fitting.fitting.least_squares.slater_density.atomic_slater_wfn."""

import numpy as np
import os
from fitting.least_squares.slater_density.atomic_slater_wfn import load_slater_wfn

__all__ = ["test_parsing_slater_density_ag",
           "test_parsing_slater_density_be",
           "test_parsing_slater_density_ne"]


def test_parsing_slater_density_be():
    # Load the Be file
    file_path = os.getcwd() + '/data/examples/be.slater'
    be = load_slater_wfn(file_path)

    assert be['configuration'] == '1S(2)2S(2)'
    assert be['energy'] == [14.57302313]

    # Check basis of S orbitals
    assert be['orbitals'] == ['1S', '2S']
    assert np.all(be['orbitals_cusp']['S'] == [1.0001235, 0.9998774])
    assert np.all(be['orbitals_energy']['S'] == [-4.7326699, -0.3092695])
    assert be['orbitals_basis']['S'] == ['1S', '1S', '1S', '1S', '1S', '1S', '2S', '1S']
    assert len(be['orbitals_occupation']) == 2
    assert be['orbitals_occupation']['1S'] == 2
    assert be['orbitals_occupation']['2S'] == 2
    assert be['orbitals_electron_array'].shape == (2, 1)
    assert (be['orbitals_electron_array'] == np.array([[2], [2]])).all()
    basis_numbers = np.array([[1], [1], [1], [1], [1], [1], [2], [1]])
    assert (be['basis_numbers']['S'] == basis_numbers).all()

    # Check exponents of S orbitals
    exponents = np.array([12.683501, 8.105927, 5.152556, 3.472467, 2.349757,
                          1.406429, 0.821620, 0.786473])
    assert (abs(be['orbitals_exp']['S'] - exponents.reshape(8, 1)) < 1.e-6).all()

    # Check coefficients of S orbitals
    coeff_1s = np.array([-0.0024917, 0.0314015, 0.0849694, 0.8685562, 0.0315855,
                         -0.0035284, -0.0004149, .0012299])
    assert be['orbitals_coeff']['1S'].shape == (8, 1)
    assert (abs(be['orbitals_coeff']['1S'] - coeff_1s.reshape(8, 1)) < 1.e-6).all()
    coeff_2s = np.array([0.0004442, -0.0030990, -0.0367056, 0.0138910, -0.3598016,
                         -0.2563459, 0.2434108, 1.1150995])
    assert be['orbitals_coeff']['2S'].shape == (8, 1)
    assert (abs(be['orbitals_coeff']['2S'] - coeff_2s.reshape(8, 1)) < 1.e-6).all()


def test_parsing_slater_density_ag():
    # Load the Ag file.
    file_path = os.getcwd() + '/data/examples/ag.slater'
    ag = load_slater_wfn(file_path)

    # Check configuration and energy.
    assert ag['configuration'] == 'K(2)L(8)M(18)4S(2)4P(6)5S(1)4D(10)'
    assert ag['energy'] == [5197.698468984]

    # Check orbitals
    assert ag['orbitals'] == ['1S', '2S', '3S', '4S', '5S', '2P', '3P', '4P', '3D', '4D']

    # Check basis
    assert ag['orbitals_basis']['P'] == ['2P', '3P', '3P', '2P', '3P', '3P', '3P',
                                         '3P', '2P', '2P', '2P']
    assert ag['orbitals_cusp']['P'] == [1.0008130, 1.0008629, 0.9998751]
    assert np.all(ag['orbitals_cusp']['D'] == [0.9991182, 1.0009214])
    assert np.all(ag['orbitals_energy']['P'] == [-125.1815809, -21.9454343, -2.6768201])

    # Check exponents of D orbitals
    exp_D = np.array([53.296212, 40.214567, 21.872645, 17.024065, 10.708021, 7.859216, 5.770205,
                      3.610289, 2.243262, 1.397570, 0.663294])
    assert (abs(ag['orbitals_exp']['D'] - exp_D.reshape(11, 1)) < 1.e-6).all()

    # Check coefficients of 3D orbital
    coeff_3D = np.array([0.0006646, 0.0037211, -0.0072310, 0.1799224, 0.5205360, 0.3265622,
                         0.0373867, 0.0007434, 0.0001743, -0.0000474, 0.0000083])
    assert (abs(ag['orbitals_coeff']['3D'] - coeff_3D.reshape(11, 1)) < 1.e-6).all()

    # Check coefficients of 4D orbital
    coeff_4D = np.array([-0.0002936, -0.0016839, 0.0092799, -0.0743431, -0.1179494, -0.2809146,
                         0.1653040, 0.4851980, 0.4317110, 0.1737644, 0.0013751])
    assert (abs(ag['orbitals_coeff']['4D'] - coeff_4D.reshape(11, 1)) < 1.e-6).all()

    # Check occupation numbers
    assert len(ag['orbitals_occupation']) == 10
    assert ag['orbitals_occupation']['1S'] == 2
    assert ag['orbitals_occupation']['2S'] == 2
    assert ag['orbitals_occupation']['3S'] == 2
    assert ag['orbitals_occupation']['4S'] == 2
    assert ag['orbitals_occupation']['5S'] == 1
    assert ag['orbitals_occupation']['2P'] == 6
    assert ag['orbitals_occupation']['3P'] == 6
    assert ag['orbitals_occupation']['4P'] == 6
    assert ag['orbitals_occupation']['3D'] == 10
    assert ag['orbitals_occupation']['4D'] == 10
    occ = np.array([2, 2, 2, 2, 1, 6, 6, 6, 10, 10])
    assert (ag['orbitals_electron_array'] == occ.reshape(10, 1)).all()


def test_parsing_slater_density_ne():
    # Load the Ne file
    file_path = os.getcwd() + '/data/examples/ne.slater'
    ne = load_slater_wfn(file_path)

    assert ne['configuration'] == "1S(2)2S(2)2P(6)"
    assert ne['energy'] == [128.547098140]

    # Check orbiral energy and cusp
    assert ne['orbitals_energy']['P'] == [-0.8504095]
    assert ne['orbitals_cusp']['P'] == [1.0000509]

    # Check basis
    assert ne['orbitals_basis']['P'] == ['3P', '2P', '3P', '2P', '2P', '2P', '2P']
    assert ne['orbitals'] == ['1S', '2S', '2P']

    # Check exponents of S orbitls

    # Check coefficients of S orbitals

    # Check exponents of P orbitals
    exp_p = np.array([25.731219, 10.674843, 8.124569, 4.295590, 2.648660, 1.710436, 1.304155])
    assert (abs(ne['orbitals_exp']['P'] - exp_p.reshape(7, 1)) < 1.e-6).all()

    # Check coefficients of P orbitals
    coeff = np.array([0.0000409, 0.0203038, 0.0340866, 0.2801866, 0.3958489, 0.3203928, 0.0510413])
    assert (abs(ne['orbitals_coeff']['2P'] - coeff.reshape(7, 1)) < 1.e-6).all()
