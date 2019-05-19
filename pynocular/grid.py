from __future__ import absolute_import
from numbers import Number
from collections import OrderedDict
from collections.abc import Iterable

import numpy as np

class Dimension(object):
    '''
    Class to hold a single dimension of a Grid
    which can have points and/or edges
    '''
    def __init__(self, var=None, edges=None, points=None, nbins=10):

        if isinstance(edges, list): edges = np.array(edges)
        if edges is not None:
            assert len(edges) > 1, 'Edges must be at least length 2'
        if isinstance(points, list): points = np.array(points)
        self.var = var
        #self._mode = mode
        #self._min = min
        #self._max = max
        #self._n_points = n_points
        #self._n_edges = n_edges
        self._edges = edges
        self._points = points
        self._nbins = nbins

    def __len__(self):
        if self._points is not None:
            return len(self._points)
        elif self._edges is not None:
            return len(self._edges) - 1
        return None

    def __str__(self):
        strs = []
        strs.append('(points) %s'%(self._points))
        strs.append('(edges)  %s'%(self._edges))
        strs.append('(nbins)  %s'%(self.nbins))
        return '\n'.join(strs)

    def __repr__(self):
        strs = []
        strs.append('Dimension("%s",'%self.var)
        strs.append('points = %s,'%(self._points.__repr__()))
        strs.append('edges = %s)'%(self._edges.__repr__()))
        strs.append('nbins = %s)'%(self.nbins))
        return '\n'.join(strs)

    @property
    def has_data(self):
        '''
        True if either edges or points are not None
        '''
        return (self._edges is not None) or (self._points is not None)
    
    @property
    def edges(self):
        if self._edges is not None:
            return self._edges
        elif self._points is not None:
            return self.edges_from_points()
        return None

    @property
    def bin_edges(self):
        '''
        just for convenience
        '''
        return self.edges

    @edges.setter
    def edges(self, edges):
        if self.has_data:
            if not len(edges) == len(self) + 1:
                raise IndexError('incompatible length of edges')
        self._edges = edges

    @property
    def points(self):
        if self._points is not None:
            return self._points
        elif self._edges is not None:
            return self.points_from_edges()
        return None

    @points.setter
    def points(self, points):
        if self.has_data:
            if not len(points) == len(self):
                raise IndexError('incompatible length of points')
        self._points = points

    @property
    def nbins(self):
        if self._points is None and self._edges is None:
            return self._nbins
        else:
            return len(self.points)

    @nbins.setter
    def nbins(self, nbins):
        if self._points is None and self._edges is None:
            self._nbins = nbins
        else:
            raise ValueError('Cannot set n since bins are already defined')

    def edges_from_points(self):
        '''
        create edges around points
        '''
        diff = np.diff(self.points)/2.
        return np.concatenate([[self.points[0]-diff[0]], self.points[:-1] + diff, [self.points[-1] + diff[-1]]])

    def points_from_edges(self):
        '''
        create points from centers between edges
        '''
        points = 0.5 * (self.edges[1:] + self.edges[:-1])
        if isinstance(points, Number):
            return np.array(points)
        return points



class Grid(object):
    '''
    Class to hold grid-like points, such as bin edges
    '''
    def __init__(self, *args, **kwargs):
        '''
        Paramters:
        ----------
        dims : Dimension or Grid object, or list thereof

        a dimesnion can also be given by kwargs
        '''
        self.dims = OrderedDict()

        for d in args:
            self.add_dim(d)

        for d,x in kwargs.items():
            if isinstance(x, int):
                self.add_dim(Dimension(var=d[0], nbins=x))
            else:
                self.add_dim(Dimension(var=d[0], edges=x))

    def add_dim(self, dim):
        '''
        add aditional Dimension

        Paramters:
        ----------
        dim : Dimension or dict or basestring

        in case of a basestring, a new empty dimension gets added
        '''
        if isinstance(dim, Dimension):
            self.dims[dim.var] = dim
        elif isinstance(dim, dict):
            dim = Dimension(**dim)
            self.add_dim(dim)
        elif isinstance(dim, str):
            new_dim = Dimension(var=dim)
            self.add_dim(new_dim)
        else:
            raise TypeError('Cannot add type %s'%type(dim))

    @property
    def initialized(self):
        '''
        wether the gri is set or not
        '''
        return self.ndim > 0 and all([edge is not None for edge in self.edges])

    @property
    def ndim(self):
        '''
        number of grid dimensions
        '''
        return len(self.dims)

    @property
    def vars(self):
        '''
        grid dimension variables
        '''
        return list(self.dims.keys())

    @property
    def edges(self):
        '''
        all edges
        '''
        return [dim.edges for dim in self.dims.values()]

    @property
    def points(self):
        '''
        all points
        '''
        return [dim.points for dim in self.dims.values()]

    @property
    def point_meshgrid(self):
        return np.meshgrid(*self.points)

    @property
    def point_mgrid(self):
        return [d.T for d in self.point_meshgrid]

    @property
    def edge_meshgrid(self):
        return np.meshgrid(*self.edges)

    @property
    def edge_mgrid(self):
        return [d.T for d in self.edge_meshgrid]

    @property
    def size(self):
        '''
        size = total number of bins / points
        '''
        return np.product([len(x) for x in self.dims.items()])

    def __len__(self):
        return self.ndim

    def __str__(self):
        '''
        string representation
        '''
        strs = []
        for dim in self.dims.items():
            strs.append('%s : %s'%dim)
        return '\n'.join(strs)

    def __repr__(self):
        strs = []
        strs.append('Grid(')
        for dim in self.dims.items():
            strs.append('%s,'%dim[1].__repr__())
        strs[-1] += ')'
        return '\n'.join(strs)

    def __iter__(self):
        '''
        iterate over dimensions
        '''
        return iter([self[n] for n in self.dims.keys()])

    @property
    def shape(self):
        '''
        shape
        '''
        shape = []
        for dim in self:
            shape.append(len(dim))
        return tuple(shape)

    def __getitem__(self, item):
        '''
        item : int, str, slice, ierable
        '''
        if isinstance(item, Number):
            return list(self.dims.values())[int(item)]
        elif isinstance(item, str):
            if not item in self.vars:
                self.add_dim(item)
            return self.dims[item]
        elif isinstance(item, Iterable):
            new_dims = []
            for it in item:
                new_dims.append(self[it])
            return self.__class__(new_dims)
        elif isinstance(item, slice):
            new_names = self.dims.keys()[item]
            return self[new_names]
        else:
            raise KeyError('Cannot get key from %s'%type(item))

    def __setitem__(self, item, val):
        raise AttributeError("to set a grid dimension, specify if it is `points` or `edges`, e.g.:\ngrid['%s'].edges = %s"%(item, val))

    def compute_indices(self, sample):
        '''
        calculate the bin indices for a a given sample
        '''
        if isinstance(sample, np.ndarray):
            assert sample.shape[0] == self.ndim
        elif isinstance(sample, list):
            assert len(sample) == self.ndim

        # array to hold indices
        indices = np.empty((self.ndim, len(sample[0])), dtype=np.int)
        #calculate bin indices
        for i in range(self.ndim):
            indices[i] = np.digitize(sample[i], self.edges[i])
        indices -= 1
        return indices


def test():
    a = Grid(var='a', edges=np.linspace(0, 1, 2))
    print(a)
    print(a.vars)
    a['x'].edges = np.linspace(0, 10, 11)
    a['y'].points = np.logspace(-1, 1, 20)
    print(a['x'].points)
    print(a['x'].edges)
    print(a['x', 'y'])

if __name__ == '__main__':
    test()
