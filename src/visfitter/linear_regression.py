#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of VisFitter.
#
#   VisFitter is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   VisFitter is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with VisFitter.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#############################################################################

# std lib imports
import logging
log = logging.getLogger(__name__)

# third party imports
from PySide import QtGui, QtCore
import numpy
import scipy.optimize


def leastSquares(x, y):
    def func(c):
        return c[0] + c[1] * x - y
    result = scipy.optimize.leastsq(func, (0, 0))
    print 'leastSquares:', result[0][0], result[0][1]
    return result[0][0], result[0][1]


def leastMedianOfSquaresCrude(x, y):
    '''
    Implementation of Crude Algorithm from [1].

    [1] J. M. Steele and W. L. Steiger, "Algorithms and complexity for least
    median of squares regression," Discrete Applied Mathematics, vol. 14,
    no. 1, pp. 93-100, May 1986.
    '''
    d_star = numpy.inf
    alpha_star = 0
    beta_star = 0

    def f(alpha, beta):
        return numpy.median(numpy.absolute((y - (alpha + beta * x))))

    n = x.size
    for ii in xrange(n):
        for jj in xrange(ii + 1, n):
            for kk in xrange(jj + 1, n):
                i, j, k = ii, jj, kk
                # renumber points so x[i] < x[j] < x[k]
                if x[i] > x[j]:
                    i, j = j, i
                if x[i] > x[k]:
                    i, k = k, i
                if x[j] > x[k]:
                    j, k = k, j
                if not ((x[i] <= x[j]) and (x[j] <= x[k])):
                    print x[i], x[j], x[k]
                    raise Exception()
                # assign beta and alpha
                if x[i] == x[k]:
                    continue
                beta = (y[i] - y[k]) / (x[i] - x[k])
                alpha = (y[j] + y[k] - beta * (x[j] + x[k])) / 2
                # get the median
                d = f(alpha, beta)
                if d < d_star:
                    d_star = d
                    alpha_star = alpha
                    beta_star = beta
    print 'leastMedianOfSquaresCrude:', alpha_star, beta_star
    return alpha_star, beta_star


def leastMedianOfSquares(x, y):
    '''
    Implementation of Algorithm 2 from [1].

    [1] J. M. Steele and W. L. Steiger, "Algorithms and complexity for least
    median of squares regression," Discrete Applied Mathematics, vol. 14,
    no. 1, pp. 93-100, May 1986.
    '''
    alpha_star, beta_star = (0, 0)
    dstar = numpy.inf
    n = x.size
    m = (n - 2) / 2
    z = numpy.empty(n)
    for r in xrange(n):
        for s in xrange(n):
            if r == s:
                continue
            d = numpy.inf
            beta = (y[r] - y[s]) / (x[r] - x[s])
            print 'beta =', beta
            zPi = []
            zN = []
            for i in xrange(n):
                z[i] = y[i] - y[r] - beta * (x[i] - x[r])
                if z[i] > 0:
                    zPi.append(z[i])
                else:
                    zN.append(z[i])
            print 'z.size = ', z.size
            print 'len(zPi) = ', len(zPi)
            print 'len(zN) = ', len(zN)
            zPi.sort()
            zN.sort()
            print 'len:', len(zPi), 'm:', m
            if m > len(zPi):
                mth_smallest_from_zPi = zPi[-1]
            else:
                mth_smallest_from_zPi = zPi[m - 1]
            if m > len(zN):
                mth_largest_from_zN = zN[0]
            else:
                mth_largest_from_zN = zN[-m]
            if abs(mth_smallest_from_zPi) < abs(mth_largest_from_zN):
                z_p = mth_smallest_from_zPi
            else:
                z_p = mth_largest_from_zN
            p = numpy.where(z==z_p)[0][0]  # get the first index
            alpha = (y[r] + y[p] - beta * (x[r] + x[p])) / 2
            if abs(z_p) < dstar:
                dstar = abs(z_p)
                alpha_star, beta_star = (alpha, beta)
    print 'leastMedianOfSquares:', alpha_star, beta_star
    return alpha_star, beta_star


def getSimpleData():
    import random
    random.seed(0)
    x = numpy.empty(30)
    y = numpy.empty(30)
    for i in xrange(30):
        x[i] = random.uniform(1, 4)
        y[i] = x[i] + 2 + random.normalvariate(0, 0.2)
    return x, y


def getRousseeuwData():
    '''
    Generates simulated x, y data as described in [1].

    [1] P. J. Rousseeuw, "Least Median of Squares Regression," Journal of the
    American Statistical Association, vol. 79, no. 388, pp. 871-880, Dec. 1984.
    '''
    import random
    random.seed(0)
    x = numpy.empty(50)
    y = numpy.empty(50)
    for i in xrange(30):
        x[i] = random.uniform(1, 4)
        y[i] = x[i] + 2 + random.normalvariate(0, 0.2)
    for i in xrange(30, 50):
        x[i] = random.normalvariate(7, 0.5)
        y[i] = random.normalvariate(2, 0.5)
    return x, y

if __name__ == '__main__':
#     x, y = getSimpleData()
    x, y = getRousseeuwData()
    import matplotlib.pyplot as plt
    plt.plot(x, y, 'ro')
    x2 = numpy.array((0, 10))

    # least (sum of) squares
    c = leastSquares(x, y)
    plt.plot(x2, c[0] + c[1] * x2, 'b-', label='LS')

    # least median of squares
    c = leastMedianOfSquaresCrude(x, y)
    plt.plot(x2, c[0] + c[1] * x2, 'g-', label='LMS')

    # Show the plot
    plt.xlim(0, 10)
    plt.ylim(0, 8)
    plt.legend(loc='best')
    plt.show()
