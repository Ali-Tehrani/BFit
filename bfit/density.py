# -*- coding: utf-8 -*-
# BFit - python program that fits a convex sum of
# positive basis functions to any probability distribution. .
#
# Copyright (C) 2020 The BFit Development Team.
#
# This file is part of BFit.
#
# BFit is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# BFit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# ---
r"""Slater Atomic Density Module."""

from bfit._slater import load_slater_wfn
import numpy as np
from scipy.special import factorial


__all__ = ["SlaterAtoms"]


class SlaterAtoms:
    r"""
    Atomic Density Class.

    Reads and Parses information from the .slater file of a atom and stores it inside this class.
    It is then able to construct the (total, core and valence) electron density based
    on linear combination of orbitals where each orbital is a linear combination of
    Slater-type orbitals.
    Elements supported by default from "./bfit/data/examples/" range from Hydrogen to Xenon.

    """

    def __init__(self, element, anion=False, cation=False):
        r"""
        Construct SlaterAtoms object.

        Parameters
        ----------
        element : str
            Symbol of element.
        anion : bool
            If true, then the anion of element is used. Some elements do not have
            anion information.
        cation : bool
            If true, then the cation of element is used. Some elements do not
            have cation information.

        """
        if not isinstance(element, str) or not element.isalpha():
            raise TypeError("The element argument should be all letters string.")
        if anion and cation:
            raise ValueError("Both anion and cation cannot be true.")

        data = load_slater_wfn(element, anion, cation)
        self._energy = data["energy"]
        self._potential_energy = data["potential_energy"]
        self._kinetic_energy = data["kinetic_energy"]
        self._configuration = data["configuration"]
        self._orbitals = data["orbitals"]
        self._orbitals_occupation = data["orbitals_occupation"]
        self._orbitals_basis = data["orbitals_basis"]
        self._basis_numbers = data["basis_numbers"]
        self._orbitals_exp = data["orbitals_exp"]
        self._orbitals_coeff = data["orbitals_coeff"]
        self._orbitals_energy = data["orbitals_energy"]
        self._orbitals_cusp = data["orbitals_cusp"]

    @property
    def energy(self):
        r"""Energy of atom."""
        return self._energy

    @property
    def kinetic_energy(self):
        r"""Kinetic energy of atom."""
        return self._kinetic_energy

    @property
    def potential_energy(self):
        r"""Potential energy of atom."""
        return self._potential_energy

    @property
    def configuration(self):
        r"""
        Return electron configuration of the element.

        For example, Beryllium returns "1S(2)2S(2)".
        """
        return self._configuration

    @property
    def orbitals(self):
        r"""
        List of strings representing each of the orbitals in the electron configuration.

        For example, Beryllium returns ["1S", "2S"] in its electron configuration.
        Ordered based on "S", "P", "D", etc.
        """
        return self._orbitals

    @property
    def orbitals_occupation(self):
        r"""
        Array returning number of electrons in each of the orbitals in the electron configuration.

        For example, Beryllium returns ndarray([[2], [2]]).
        """
        return self._orbitals_occupation

    @property
    def orbitals_basis(self):
        r"""
        Return grouping of Slater-type orbitals to the type ("S", "P", ...).

        Dictionary mapping type of orbital (e.g. "S", "P") to the number
        and type of the :math:`N` Slater-type orbitals. For example, Helium could
        map "S" to ['2S', '1S', '1S', '1S', '2S'].
        """
        return self._orbitals_basis

    @property
    def basis_numbers(self):
        r"""
        Return type of Slater-type orbital to the type, e.g. "S".

        Dictionary mapping type of orbital (e.g. "S", "P") to array
        containing :math:`n` of the :math:`N` Slater-type orbital. These play the
        role of the principal quantum number to each Slater-type orbital.
        """
        return self._basis_numbers

    @property
    def orbitals_exp(self):
        r"""
        Exponent of each Slater-type orbital grouped by type of orbital.

        Dictionary mapping type of orbitals (e.g. "S", "P") to the
        exponent of each of the :math:`N` Slater-type orbital.
        """
        return self._orbitals_exp

    @property
    def orbitals_coeff(self):
        r"""
        Coefficients of each Slater-type orbital grouped by type of orbital.

        Dictionary mapping type of orbitals (e.g. "S", "P") to
        the coefficients of the :math:`N` Slater-type orbitals.
        """
        return self._orbitals_coeff

    @property
    def orbitals_energy(self):
        r"""Energy of each of the :math:`N` Slater-type orbital."""
        return self._orbitals_energy

    @property
    def orbitals_cusp(self):
        r"""
        Cusp values of each of the N Slater-type orbital.

        Same ordering as `orbitals`. Does not exist for Heavy atoms past Xenon.
        """
        return self._orbitals_cusp

    @staticmethod
    def slater_orbital(exponent, number, points):
        r"""
        Compute the Slater-type orbitals on the given points.

        A Slater-type orbital is defined as:
        .. math::
            R(r) = N r^{n-1} e^{- C r)

        where,
            :math:`n` is the principal quantum number of that orbital.
            :math:`N` is the normalizing constant.
            :math:`r` is the radial point, distance to the origin.
            :math:`\zeta` is the zeta exponent of that orbital.

        Parameters
        ----------
        exponent : ndarray, (M, 1)
            The zeta exponents :math:`\zeta` of :math:`M` Slater orbitals.
        number : ndarray, (M, 1)
            The principal quantum numbers :math:`n` of :math:`M` Slater orbitals.
        points : ndarray, (N,)
            The radial :math:`r` grid points.

        Returns
        -------
        slater : ndarray, (N, M)
            The :math:`M` Slater-type orbitals evaluated on :math:`N` grid points.

        See Also
        --------
        - The principal quantum number of all of the orbital are stored in `basis_numbers`.
        - The zeta exponents of all of the orbitals are stored in the attribute `orbitals_exp`.

        """
        if points.ndim != 1:
            raise ValueError("The argument point should be a 1D array.")
        # compute norm & pre-factor
        norm = np.power(2. * exponent, number) * np.sqrt((2. * exponent) / factorial(2. * number))
        pref = np.power(points, number - 1).T
        # compute slater function
        slater = norm.T * pref * np.exp(-exponent * points).T
        return slater

    def phi_matrix(self, points, deriv=False):
        r"""
        Compute the linear combination of Slater-type atomic orbitals on the given points.

        Each row corresponds to a point on the grid, represented as :math:`r` and
         each column is represented as a linear combination of Slater-type atomic orbitals
         of the form:

        .. math::
            \sum_{i=1}^{K-1} c_i R(r, n_i, C_i)

        where,
            :math:`c_i` is the coefficient of the Slater-type orbital,
            :math:`\zeta_i` is the zeta exponent attached to the Slater-type orbital,
            :math:`n_i` is the principal quantum number attached to the Slater-type orbital,
            :math:`R(r, n_i, C_i)` is the Slater-type orbital,
            :math:`K` is the number of orbitals.

        Parameters
        ----------
        points : ndarray, (N,)
            The radial grid points.
        deriv : bool
            If true, use the derivative of the slater-orbitals.

        Returns
        -------
        phi_matrix : ndarray(N, K)
            The linear combination of Slater-type orbitals evaluated on the grid points.
            The order is S orbitals, then P then D.

        Notes
        -----
        - At r = 0, the derivative of slater-orbital is undefined and this function returns
            zero instead. See "derivative_slater_type_orbital".

        """
        # compute orbital composed of a linear combination of Slater
        phi_matrix = np.zeros((len(points), len(self.orbitals)))
        for index, orbital in enumerate(self.orbitals):
            exps, number = self.orbitals_exp[orbital[1]], self.basis_numbers[orbital[1]]
            if deriv:
                slater = self.derivative_slater_type_orbital(exps, number, points)
            else:
                slater = self.slater_orbital(exps, number, points)
            phi_matrix[:, index] = np.dot(slater, self.orbitals_coeff[orbital]).ravel()
        return phi_matrix

    def atomic_density(self, points, mode="total"):
        r"""
        Compute atomic density on the given points.

        The total density is written as a linear combination of Slater-type orbital
        whose coefficients is the orbital occupation number of the electron configuration:
        .. math::
            \sum n_i |P(r, n_i, C_i)|^2

        where,
            :math:`n_i` is the number of electrons in orbital i.
            :math:`P(r, n_i, C_i)` is a linear combination of Slater-type orbitals evaluated
                on the point :math:`r`.

        For core and valence density, please see More Info below.

        Parameters
        ----------
        points : ndarray, (N,)
            The radial grid points.
        mode : str
            The type of atomic density, which can be "total", "valence" or "core".

        Returns
        -------
        dens : ndarray, (N,)
            The atomic density on the grid points.

        Notes
        -----
        The core density and valence density is respectively written as:
        .. math::
            \sum n_i (1 - e^{-|e_i - e_{homo}|^2}) |P(r, n_i, C_i)|
            \sum n_i e^{-|e_i - e_{homo}|^2}) |P(r, n_i. C_i)|

        where,
            :math:`e_i` is the energy of the orbital i.
            :math:`e_{HOMO}` is the energy of the highest occupying orbital.

        """
        if mode not in ["total", "valence", "core"]:
            raise ValueError("Argument mode not recognized!")

        # compute orbital occupation numbers
        orb_occs = self.orbitals_occupation
        if mode == "valence":
            orb_homo = self.orbitals_energy[len(self.orbitals_occupation) - 1]
            orb_occs = orb_occs * np.exp(-(self.orbitals_energy - orb_homo)**2)
        elif mode == "core":
            orb_homo = self.orbitals_energy[len(self.orbitals_occupation) - 1]
            orb_occs = orb_occs * (1. - np.exp(-(self.orbitals_energy - orb_homo)**2))
        # compute density
        dens = np.dot(self.phi_matrix(points)**2, orb_occs).ravel() / (4 * np.pi)
        return dens

    @staticmethod
    def derivative_slater_type_orbital(exponent, number, points):
        r"""
        Compute the derivative of Slater-type orbitals on the given points.

        A Slater-type orbital is defined as:
        .. math::
            \frac{d R(r)}{dr} = \bigg(\frac{n-1}{r} - C \bigg) N r^{n-1} e^{- C r),

        where,
            :math:`n` is the principal quantum number of that orbital.
            :math:`N` is the normalizing constant.
            :math:`r` is the radial point, distance to the origin.
            :math:`C` is the zeta exponent of that orbital.

        Parameters
        ----------
        exponent : ndarray, (M, 1)
            The zeta exponents of Slater orbitals.
        number : ndarray, (M, 1)
            The principle quantum numbers of Slater orbitals.
        points : ndarray, (N,)
            The radial grid points. If points contain zero, then it is undefined at those
            points and set to zero.

        Returns
        -------
        slater : ndarray, (N, M)
            The Slater-type orbitals evaluated on the grid points.

        Notes
        -----
        - At r = 0, the derivative is undefined and this function returns zero instead.

        References
        ----------
        See wikipedia page on "Slater-Type orbitals".

        """
        slater = SlaterAtoms.slater_orbital(exponent, number, points)
        # Consider the case when dividing by zero.
        with np.errstate(divide='ignore'):
            # derivative
            deriv_pref = (number.T - 1.) / np.reshape(points, (points.shape[0], 1)) - exponent.T
            deriv_pref[np.abs(points) < 1e-10, :] = 0.0
        deriv = deriv_pref * slater
        return deriv

    def lagrangian_kinetic_energy(self, points):
        r"""
        Positive definite or Lagrangian kinetic energy density.

        Parameters
        ----------
        points : ndarray,(N,)
            The radial grid points.

        Returns
        -------
        energy : ndarray, (N,)
            The kinetic energy on the grid points.

        Notes
        -----
        - This sets kinetic energy value at :math:`r=0` to zero.
        """
        kinetic = np.zeros((len(points),))
        orbital_to_angular = {
            "S": 0.0, "P": 2.0, "D": 6.0, "F": 12.0
        }
        # The following integrals are obtained from Slater-Type orbital from Wikiepdia.
        #  The formula between two slater-type orbitals with numbers nlm, and numbers qkp is
        #   $\delta_{lk}\delta_{mp} e^(-(\alpha_1 + \alpha_2) r * \bigg[
        #       [k(k + 1) - q(q-1)]r^{n+q-2.0} + 2\alpha_2 q r^{n + q - 1.0} - \alpha_2^2r^{n + q}
        #   bigg] / 2.0$
        for index, orbital in enumerate(self.orbitals):
            exps, number = self.orbitals_exp[orbital[1]], self.basis_numbers[orbital[1]]
            angular = orbital_to_angular[orbital[1]]  # Angular number l(l + 1)

            # Calculate  e^(-(\alpha_1 + \alpha_2) r * coeffs_1 * coeffs_2 * norm_1 * norm_2
            norm = np.ravel(
                np.power(2. * exps, number) * np.sqrt((2. * exps) / factorial(2. * number))
            )
            coeffs_norm = np.einsum("i,i,j,j->ij", np.ravel(self.orbitals_coeff[orbital]),
                                    norm, np.ravel(self.orbitals_coeff[orbital]), norm)
            exps_comb = exps + np.ravel(exps)
            exponential = np.exp(-1.0 * np.einsum("ij,k->ijk", exps_comb, points))
            combination = np.einsum("ijk,ij->ijk", exponential, coeffs_norm)
            number_combs = number + np.ravel(number)

            # Calculate [k(k + 1) - q(q-1)]r^{n+q-2.0}
            points_power = points[:, None, None]**(number_combs - 2.0)
            first_term = np.einsum(
                "i,kij->ijk", np.ravel(angular - number * (number - 1.0)), points_power
            )
            # Calculate + 2\alpha_2 q r^{n + q - 1.0}
            points_power = points[:, None, None]**(number_combs - 1.0)
            second_term = np.einsum(
                "j,j,kij->ijk", 2.0 * np.ravel(exps), np.ravel(number), points_power
            )
            # Calculate - \alpha_2^2r^{n + q}
            points_power = points[:, None, None]**(number_combs)
            third_term = np.einsum("i,kij->ijk", np.ravel(exps)**2.0, points_power)

            combination = combination * (first_term + second_term - third_term)
            kinetic += np.einsum("ijk->k", combination) * self.orbitals_occupation[index]
        # Divide by r^2 and set division by zero to zero.
        with np.errstate(divide='ignore'):
            kinetic /= (points ** 2.0)
            kinetic[np.abs(points) < 1e-10] = 0.
        return kinetic / (2.0 * 4.0 * np.pi)

    def derivative_density(self, points):
        r"""
        Return the derivative of the atomic density on a set of points.

        Parameters
        ----------
        points : ndarray,(N,)
            The radial grid points.

        Returns
        -------
        deriv : ndarray, (N,)
            The derivative of atomic density on the grid points.
        """
        factor = self.phi_matrix(points) * self.phi_matrix(points, deriv=True)
        derivative = np.dot(2. * factor, self.orbitals_occupation).ravel() / (4 * np.pi)
        return derivative
