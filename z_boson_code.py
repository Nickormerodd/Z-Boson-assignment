# -*- coding: utf-8 -*-
"""
PHYS20161- Z boson assignment

This code reads in data files as listed (line 18 and 19), deletes any nans
or unacceptable invalid and anomolous values (to a 3 sigma limit), and creates
useful plots, as well as telling the user what the reduced chi squared is by
minimising two parameters in a function and giving those values.

Nick Ormerod 14/12/21
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import hbar, e

FILE_NAME_1 = 'z_boson_data_1.csv'
FILE_NAME_2 = 'z_boson_data_2.csv'

GUESS_MASS = 90
GUESS_WIDTH = 3 # guesses used as fitted coefficients on initial fit
GUESS_PARAMETERS = GUESS_MASS, GUESS_WIDTH

def validate_data(data_uncorrected, file_name):
    """
    Parameters
    ----------
    data_uncorrected : array
    file_name : string

    Returns
    ----------
    data_corrected_unordered : array

    """
    data_uncorrected = np.genfromtxt(file_name, delimiter = ',', skip_header=1)
    temp_1 = data_uncorrected[~np.isnan(data_uncorrected[:,0])]
    temp_2 = temp_1[~np.isnan(temp_1[:,1])]
    data_no_nans = temp_2[~np.isnan(temp_2[:,2])]

    data_corrected_unordered = []
    for i in range(len(data_no_nans)):
        if data_no_nans[i][0] > 0 and data_no_nans[i][1] > 0 and data_no_nans[i][2] > 0:
            data_corrected_unordered.append(data_no_nans[i])

    return data_corrected_unordered

def correct_data(name_data_1, name_data_2):
    """
    collects data, validates it, then orders it

    Parameters
    -------
    name_data_1 : string
    name_data_2: string

    Returns
    -------
    outlier_data_sorted : array

    """
    data_1_uncorrected = np.genfromtxt(name_data_1, delimiter = ',', skip_header=1)
    data_2_uncorrected = np.genfromtxt(name_data_2, delimiter = ',', skip_header=1)

    data_1_corrected = validate_data(data_1_uncorrected, name_data_1)
    data_2_corrected = validate_data(data_2_uncorrected, name_data_2)
    outlier_data_unordered = np.vstack((data_1_corrected, data_2_corrected))
    outlier_data_ordered = outlier_data_unordered[np.argsort(outlier_data_unordered[:,0]
                                                             , axis = 0)]

    return outlier_data_ordered

def function(energy, mass, width):
    """
    Parameters
    -----------
    energy : float
    mass : float
    width : float

    Returns
    ----------
    (12*pi/coefficient_mass_variable**2) * x_variable**2 * partial_width_Z /
    [ (x_variable**2 - coefficient_mass_variable**2)**2 +
     coefficient_mass_variable**2 * coefficient_width_variable**2 ]

    """
    partial_width_z = 83.91/1000  # a constant of the equation in units Gev

    return ((12* np.pi / mass**2 ) * energy**2 * partial_width_z**2 /
            (((energy**2 - mass**2)**2 + (mass**2 * width**2))) * 0.3894e6)

def remove_anomoly(x_data, y_data, uncertainty_data, parameter_coefficients, sigma_value):
    """
    Parameters
    ----------
    x_data : array
    y_data : array
    uncertainty_data : array
    mass_coefficient : float
    width_coefficient : float
    sigma_value : float, chosen to the desired value of uncertainty

    Returns
    -------
    data_filtered : array, new array with anomolies removed to the value of sigma

    """

    data_filtered = np.zeros((0, 3))
    mass_coefficient, width_coefficient = parameter_coefficients

    for i in range(len(x_data)):
        x_temp = x_data[i]
        y_temp = y_data[i]
        uncertainty_temp = uncertainty_data[i]

        if np.abs(function(x_temp, mass_coefficient,
                           width_coefficient) - y_temp) <= sigma_value*uncertainty_temp:

            data_check = np.array([x_temp, y_temp, uncertainty_temp])
            data_filtered = np.vstack((data_filtered, data_check))
    return data_filtered

def estimating_parameters(data):
    """
    uses curve_fit function to estimate paramters

    Parameters
    ----------
    data: array

    Returns
    -------
    end_data : array, a data with a different sigma value than the first
    end_parameter: array, with two floats
    uncertainties : array, with two floats

    """
    parameter_estimates, *covariance_1 = curve_fit(function, data[:,0], data[:,1],
                                                p0=(GUESS_MASS, GUESS_WIDTH), maxfev= 1000)
    _ = covariance_1
    end_data = remove_anomoly(data[:,0], data[:,1], data[:,2],
                                   parameter_estimates, 3)
    #finished data with no anomolies
    end_parameters, *covariance_2 = curve_fit(function, end_data[:,0],
                                    end_data[:,1], p0=(parameter_estimates),
                                maxfev= 1000, sigma= end_data[:,2], absolute_sigma= True)

    x_uncertainty = np.sqrt(covariance_2[0][0][0])
    y_uncertainty = np.sqrt(covariance_2[0][1][1])
    uncertainties = x_uncertainty, y_uncertainty

    return end_data, end_parameters, uncertainties

def chi_squared(energy, mass_estimate, width_estimate, cross_section, uncertainties):
    """
    Parameters
    ---------
    coefficient_mass_variable (float)
    coefficient_width_variable (float)
    x_values array of floats
    function_data array of floats
    errors array of floats

    Returns
    ---------
    chi squared : float, after comparing function and data for a given coefficient

    """

    prediction = function(energy, mass_estimate, width_estimate)

    return np.sum(((prediction - cross_section) / uncertainties)**2)

def initial_graph_plot():
    """
    plots energy against cross section and energy against a function with trial values

    Returns
    -------
    None

    """
    fig_1 = plt.figure()
    ax_1 = fig_1.add_subplot(321)

    ax_1.set_title('function against cross section', fontsize=8, color='black')
    ax_1.set_xlabel('function- Energy/ GeV', fontsize=9, color='r')
    ax_1.set_ylabel('cross section/ nb', fontsize=9, color='r')
    ax_1.plot(data_30sigma[:,0], function(data_30sigma[:,0], GUESS_MASS, GUESS_WIDTH), 'o')

    ax_2 = fig_1.add_subplot(322)

    ax_2.set_title(r'energy against cross section with anomolies', fontsize=8, color='black')
    ax_2.set_xlabel('energy data/ GeV', fontsize=9, color='r')
    ax_2.set_ylabel('cross section/ nb', fontsize=9, color='r')
    ax_2.plot(data_30sigma[:,0], data_30sigma[:,1], 'o')

    plt.savefig('cross_section_vs_data.png', dpi=600)
    fig_1.tight_layout()

    #initial fit

    ax_3 = fig_1.add_subplot(312)

    ax_3.set_title(r'initial fit with anomoly: $\sigma$ = 30', fontsize=12, color='black')
    ax_3.set_xlabel('energy GeV', fontsize=8, color='r')
    ax_3.set_ylabel('cross section / nb', fontsize=8, color='r')

    ax_3.plot(data_30sigma[:,0], function(data_30sigma[:,0], GUESS_MASS, GUESS_WIDTH),
              'o', color = 'orange', label = 'function')
    ax_3.plot(data_30sigma[:,0], data_30sigma[:,1], 'o', color = 'blue')
    ax_3.errorbar(data_30sigma[:,0], data_30sigma[:,1], data_30sigma[:,2]*3, fmt='.',
                  color = 'blue', label = 'data')
    ax_3.legend()
    plt.savefig('initial_fit.png', dpi=600)
    fig_1.tight_layout()

    plt.show()

def plot_final_fit():
    """
    Plots the fit against the data with refined estimates for width and mass

    Returns
    -------
    None.

    """
    fig_3 = plt.figure()
    ax_4 = fig_3.add_subplot(111)

    ax_4.set_title(r'final fit: $\sigma$ = 3', fontsize=16, color='black')
    ax_4.set_xlabel('energy GeV', fontsize=10, color='r')
    ax_4.set_ylabel('cross section / nb', fontsize=10, color='r')

    fit_data = estimating_parameters(data_30sigma)[0]
    final_mass, final_width = estimating_parameters(data_30sigma)[1]

    ax_4.plot(fit_data[:,0], function(fit_data[:,0], final_mass , final_width),
              '--', dashes = [3,3], color = 'red', label = 'Line of best fit')
    ax_4.plot(finished_data[:,0], finished_data[:,1], 'o', color = 'green', alpha = 0.5)
    ax_4.errorbar(finished_data[:,0], finished_data[:,1], finished_data[:,2]*3, fmt='.',
                  alpha = 0.5, color = 'black', label = 'data points with errors')
    ax_4.legend()
    plt.savefig('final_fit.png', dpi=600)
    fig_3.tight_layout()

def contour_plots(x_min, y_min):
    """
    plots a contour plot of mass against width against Z-
    where Z is a 2D array of chi squared values for each i and j in a mesh grid
    then plots a 3D contour plot

    Returns
    -------
    None.

    """
    x_mesh = np.linspace(x_min -0.2, x_min +0.2, 100)
    y_mesh = np.linspace(y_min -0.2, y_min +0.2, 100)
    x_grid, y_grid = np.meshgrid(x_mesh, y_mesh)
    # makes a grid mesh of corresponding x and y values

    chi2 = np.empty((0, len(x_mesh)))   # calculate chi-square over parameter grid

    for j in y_mesh:
        temp = np.array([])
        for i in x_mesh:
            chi2_value = chi_squared(finished_data[:,0], i, j, finished_data[:,1],
                                     finished_data[:,2])/(len(finished_data[:,0])-1)
            temp = np.append(temp, chi2_value)
        chi2 = np.vstack((chi2, temp))

    fig_4 = plt.figure(figsize=(6, 6))
    ax_5 = fig_4.add_subplot(111)
    ax_5.set_title('Minimised mass and width plotted against reduced chi squared')
    ax_5.set_xlabel('Mass/ GeV/c^2')
    ax_5.set_ylabel('Width/ GeV')
    contour_plotf = ax_5.contourf(x_grid, y_grid, chi2, levels = [0,1,1.5,2,3,4,5,6,7], cmap ='hot')
    contour_plot = ax_5.contour(x_grid, y_grid, chi2, levels = [0,1,1.5,2,3,4,5,6,7])
    fig_4.colorbar(contour_plotf)
    ax_5.clabel(contour_plot, fontsize= 10, colors ='black')
    final_mass, final_width = estimating_parameters(data_30sigma)[1]
    ax_5.plot(final_mass, final_width, 'o', color = 'w', label = 'observed value')
    ax_5.legend()

    plt.savefig('contour_plot.png', dpi=600)
    plt.show()

    # 3D PLOT

    fig_5 = plt.figure()
    ax_6 = plt.axes(projection = '3d')

    contour_3d_plotf = ax_6.contour3D(x_grid, y_grid, chi2, 50)
    fig_5.colorbar(contour_3d_plotf)
    ax_6.set_title('3D plot of mass against width against reduced chi squared')
    ax_6.set_xlabel('Mass/ GeV/c^2')
    ax_6.set_ylabel('Width/ GeV')
    ax_6.set_zlabel('Reduced chi2 value')
    ax_6.plot(final_mass, final_width, np.min(chi2), 'o', color = 'r', label = 'observed value')
    ax_6.legend()

    ax_6.view_init(5,20)

    plt.savefig('3D_contour_plot.png', dpi=600)
    plt.show()

def main():
    """
    runs the main code and prints appropriate statements

    Returns
    -------
    0 : int, to represent a successful code running

    """
    final_mass, final_width = final_parameters
    mass_uncertainty, width_uncertainty = final_uncertainties

    initial_graph_plot()
    plot_final_fit()
    contour_plots(final_mass, final_width)

    chi2_answer = chi_squared(finished_data[:,0], final_mass, final_width,
                                 finished_data[:,1], finished_data[:,2])
    reduced_chi2 = chi2_answer/ (len(finished_data[:,0])-1)

    lifetime = hbar / (final_width * e * 1e9)
    lifetime_uncertainty = width_uncertainty * lifetime / final_width

    print('The minimised mass of the Z boson is {0:#.4g} +/- {1:#.1g} GeV/c^2 and'
          ' the minimised width is {2:#.4g} +/- {3:#.2g} GeV, which gives a lifetime'
          ' of {4:#.3g} +/- {5:#.3g} s'.format(final_mass, mass_uncertainty, final_width,
                  width_uncertainty, lifetime, lifetime_uncertainty))

    print('The chi squared, for the function, given the data, is {0:#.3g}, which,'
          ' with a data set of length {1}, gives a reduced chi squared of {2:#.3g}'.format(
        chi2_answer, len(finished_data[:,0]), reduced_chi2))

    return 0

outlier_data = correct_data(FILE_NAME_1, FILE_NAME_2)

data_30sigma = remove_anomoly(outlier_data[:,0], outlier_data[:,1], outlier_data[:,2],
                              GUESS_PARAMETERS, 30)

finished_data, final_parameters, final_uncertainties = estimating_parameters(data_30sigma)

if __name__ == '__main__':
    main()
