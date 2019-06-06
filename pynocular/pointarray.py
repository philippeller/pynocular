from __future__ import absolute_import
import numpy as np
import pandas
import pynocular as pn
import pynocular.plotting
from pynocular.data import Data
from pynocular.utils.formatter import format_html
import tabulate

__license__ = '''Copyright 2019 Philipp Eller

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''


class PointArray(object):
    '''Structure to hold a single PointData item
    '''
    def __init__(self, *args, **kwargs):
        '''Instantiate a data dimension'''
        if len(args) == 0 and len(kwargs) == 0:
            self.data = None
            self.name = None
        elif len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], pandas.core.series.Series):
                self.data = args[0]
                self.name = args[0].name
            elif isinstance(args[0], dict) and len(args[0]) == 1:
                self.data = args[0].values()[0]
                self.name = args[0].keys()[0]
            else:
                raise ValueError()
        elif len(args) == 2 and len(kwargs) == 0:
            self.data = args[1]
            self.name = args[0]
        elif len(args) == 0 and len(kwargs) == 1:
            self.data = kwargs[0].values()[0]
            self.name = kwargs[0].keys()[0]
        else:
            raise ValueError("Did not understand input arguments")

    @property
    def type(self):
        if isinstance(self.data, pandas.core.series.Series):
            return 'df'
        elif isinstance(self.data, np.ndarray):
            return 'simple'

    def __repr__(self):
        return 'PointDataDim(%s : %s)'%(self.name, self.data)

    def _repr_html_(self):
        '''for jupyter'''
        if self.type == 'df':
            return None
        else:
            return format_html(self)

    def __str__(self):
        return '%s : %s'%(self.name, self.data)

    def __add__(self, other):
        return np.add(self, other)
    def __sub__(self, other):
        return np.subtract(self, other)
    def __mul__(self, other):
        return np.multiply(self, other)
    def __truediv__(self, other):
        return np.divide(self, other)
    def __pow__(self, other):
        return np.power(self, other)
    def __lt__(self, other):
        return np.less(self, other)
    def __le__(self, other):
        return np.less_equal(self, other)
    def __eq__(self, other):
        return np.equal(self, other)
    def __ne__(self, other):
        return np.not_equal(self, other)
    def __gt__(self, other):
        return np.greater(self, other)
    def __ge__(self, other): 
        return np.greater_equal(self, other)

    def __array__(self):
        return self.values

    @property
    def values(self):
        if self.type == 'df':
            return self.data.values
        return self.data

    def __array_wrap__(self, result, context=None):
        if isinstance(result, np.ndarray):
            if result.ndim > 0 and result.shape[0] == len(self):
                if self.type == 'df':
                    new_data = pandas.core.series.Series(result)
                    new_data.name = self.name
                    new_obj = pn.PointDataDim(new_data)
                else:
                    new_obj = pn.PointDataDim()
                    new_obj.data = result
                    new_obj.name = self.name
                return new_obj
            if result.ndim == 0:
                return np.asscalar(result)
        return result

    def __len__(self):
        return self.data.shape[0]

