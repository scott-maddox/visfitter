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
import numpy


class AbstractParser(object):
    def __init__(self, f):
        self.f = f

    def parse(self):
        raise NotImplementedError()

def getXY(filepath, xcol=0, ycol=1, sep=None):
    x = []
    y = []
    with open(filepath, 'rU') as f:
        # Find the first parser that accepts the input
        for line in f:
            try:
                if sep is None:
                    tokens = line.split()
                else:
                    tokens = line.split(sep)
                x.append(float(tokens[xcol]))
                y.append(float(tokens[ycol]))
            except:
                continue
    x = numpy.array(x)
    y = numpy.array(y)
    log.debug('x = {}'.format(x))
    log.debug('y = {}'.format(y))
    return x, y