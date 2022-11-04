# Z-Boson-assignment
Minimisation of two variables with a chi squared matrix...

This code takes energy and cross sectional data for Z Bosons in the LHC, deletes any nans
or unacceptable, invalid and anomolous values (to a 3 sigma limit), and creates
useful plots, as well as telling the user what the reduced chi squared is by
minimising two parameters in a function and giving those values.

The code provides 4 plots: An inital plot of a long polynomial multivariate function, the data given, plotted, and an inital 30 sigma fit; a final 3 sigma fit to reduce anomolies; a 2D chi squared contour plot, minimising both variables; a 3D chi squared contour plot to easily visualize what is happening.

The minimised variables are calculated by plotting one variable against (and then both) against a 2D mesh grid array of corresponding chi squared values for each i and j.

The codes other output is the data, obtained in a paragraph such as:
"The minimised mass of the Z boson is 91.18 +/- 0.01 GeV/c^2 and the minimised width is 2.509 +/- 0.014 GeV, which gives a lifetime of 2.62e-25 +/- 1.47e-27 s
The chi squared, for the function, given the data, is 87.1, which, with a data set of length 94, gives a reduced chi squared of 0.937"
