
import numpy as np

from six.moves import map, range, reduce, zip
from itertools import chain, tee
from functools import partial
from operator import mul

def couple(f, g):
    """
    Given a pair of functions that take the same arguments, return a 
    single function that returns a pair consisting of the return values 
    of each function.

    Notes
    -----
    Equivalent to::

        lambda f, g: lambda *args, **kwargs: (f(*args, **kwargs), g(*args, **kwargs))

    Examples
    --------
    >>> f = lambda x: 2*x**3
    >>> df = lambda x: 6*x**2
    >>> f_new = couple(f, df)
    >>> f_new(5)
    (250, 150)

    """
    def coupled(*args, **kwargs):
        return f(*args, **kwargs), g(*args, **kwargs)
    return coupled

def decouple(fn):
    """
    Examples
    --------
    >>> h = lambda x: (2*x**3, 6*x**2)
    >>> f, g = decouple(h)
    
    >>> f(5)
    250
    
    >>> g(5)
    150
    """
    def fst(*args, **kwargs):
        return fn(*args, **kwargs)[0]

    def snd(*args, **kwargs):
        return fn(*args, **kwargs)[1]

    return fst, snd

def nwise(iterable, n):
    """
    Iterator that acts like a sliding window of size `n`; slides over
    some iterable `n` items at a time. If iterable has `m` elements, 
    this function will return an iterator over `m-n+1` tuples.

    Parameters
    ----------
    iterable : iterable
        An iterable object.
    
    n : int
        Window size.
    
    Returns
    -------
    iterator of tuples.
        Iterator of size `n` tuples 

    Notes
    -----
    First `n` iterators are created::

        iters = tee(iterable, n)

    Next, iterator `i` is advanced `i` times::

        for i, it in enumerate(iters):
            for _ in range(i):
                next(it, None)

    Finally, the iterators are zipped back up again::

        return zip(*iters)

    Examples
    --------

    >>> a = [2, 5, 7, 4, 2, 8, 6]

    >>> list(nwise(a, n=3))
    [(2, 5, 7), (5, 7, 4), (7, 4, 2), (4, 2, 8), (2, 8, 6)]

    >>> pairwise = partial(nwise, n=2)
    >>> list(pairwise(a))
    [(2, 5), (5, 7), (7, 4), (4, 2), (2, 8), (8, 6)]

    >>> list(nwise(a, n=1))
    [(2,), (5,), (7,), (4,), (2,), (8,), (6,)]

    >>> list(nwise(a, n=7))
    [(2, 5, 7, 4, 2, 8, 6)]

    .. todo::

       These should probably raise `ValueError`...

    >>> list(nwise(a, 8))
    []

    >>> list(nwise(a, 9))
    []

    A sliding window of size `n` over a list of `m` elements
    gives `m-n+1` windows 

    >>> len(a) - len(list(nwise(a, 2))) == 1
    True

    >>> len(a) - len(list(nwise(a, 3))) == 2
    True

    >>> len(a) - len(list(nwise(a, 7))) == 6
    True
    """

    iters = tee(iterable, n)
    for i, it in enumerate(iters):
        for _ in range(i):
            next(it, None)
    return zip(*iters)

pairwise = partial(nwise, n=2)

def flatten(*arys, order='C', returns_shapes=True):
    """
    Flatten a variable number of ndarrays and/or numpy scalars (0darray) 
    of possibly heterogenous dimensions and shapes and concatenate them 
    together into a flat (1d) array.

    .. note::

       Not to be confused with `np.ndarray.flatten()` (a more befitting
       might be `chain` or `stack` or maybe something else entirely 
       since this function is more than either `concatenate` or 
       `np.flatten` itself. Rather, it is the composition of the former 
       with the latter.

    Parameters
    ----------
    arys1, arys2, ... : array_like
        One or more input arrays of possibly heterogenous shapes and 
        sizes.

    order : {‘C’, ‘F’, ‘A’}, optional
        Whether to flatten in C (row-major), Fortran (column-major) 
        order, or preserve the C/Fortran ordering. The default is ‘C’.
    
    returns_shapes : bool, optional 
        Default is `True`. If `True`, the tuple `(flattened, shapes)` is 
        returned, otherwise only `flattened` is returned.

    Returns
    -------

    .. todo:: 

       For consistency, might consider keeping with the Python 3 theme 
       of returning generators everywhere... Especially since most other 
       functions here does...

    flattened,[shapes] : {1darray, list of tuples}
        Return the flat (1d) array resulting from the concatenation of 
        flattened ndarrays. When `returns_shapes` is `True`, return a 
        list of tuples containing also the shapes of each array as the 
        second element.

    See Also
    --------
    pyalacarte.utils.unflatten : its inverse

    Notes
    -----
    Equivalent to::

        lambda *arys, order='C', returns_shapes=True: (np.hstack(map(partial(np.ravel, order=order), ndarrays)), list(map(np.shape, ndarrays))) if returns_shapes else np.hstack(map(partial(np.ravel, order=order), ndarrays))

    This implementation relies on the fact that scalars are treated as
    0-dimensional arrays. That is,

    >>> a = 4.6
    >>> np.ndim(a)
    0
    >>> np.shape(a)
    ()

    >>> np.ravel(a)
    array([ 4.6])

    Note also that the following is also a 0-dimensional array

    >>> b = np.array(3.14)
    >>> np.ndim(b)
    0
    >>> np.shape(b)
    ()

    .. important::

       When 0-dimensional arrays of the latter form are flattened, 
       *they  will be unflattened as a scalar*. (Because special cases 
       aren't special enough to break the rules.)

    Examples
    --------
    >>> a = 9
    >>> b = np.array([4, 7, 4, 5, 2])
    >>> c = np.array([[7, 3, 1],
    ...               [2, 6, 6]])
    >>> d = np.array([[[6, 5, 5],
    ...                [1, 6, 9]],
    ...               [[3, 9, 1],  
    ...                [9, 4, 1]]])
    
    >>> flatten(a, b, c, d) # doctest: +NORMALIZE_WHITESPACE
    (array([9, 4, 7, 4, 5, 2, 7, 3, 1, 2, 6, 6, 6, 5, 5, 1, 6, 9, 3, 9, 
            1, 9, 4, 1]), [(), (5,), (2, 3), (2, 2, 3)])

    >>> flatten(a, b, c, d, order='F') 
    ... # doctest: +NORMALIZE_WHITESPACE
    (array([9, 4, 7, 4, 5, 2, 7, 2, 3, 6, 1, 6, 6, 3, 1, 9, 5, 9, 6, 4, 
            5, 1, 9, 1]), [(), (5,), (2, 3), (2, 2, 3)])

    Note that scalars and 0-dimensional arrays are treated differently 
    from 1-dimensional singleton arrays.

    >>> flatten(3.14, np.array(2.71), np.array([1.61])) 
    ... # doctest: +NORMALIZE_WHITESPACE
    (array([ 3.14,  2.71,  1.61]), [(), (), (1,)])

    >>> flatten(a, b, c, d, returns_shapes=False) 
    ... # doctest: +NORMALIZE_WHITESPACE
    array([9, 4, 7, 4, 5, 2, 7, 3, 1, 2, 6, 6, 6, 5, 5, 1, 6, 9, 3, 9, 
           1, 9, 4, 1])

    >>> flatten(a, b, c, d, order='F', returns_shapes=False) 
    ... # doctest: +NORMALIZE_WHITESPACE
    array([9, 4, 7, 4, 5, 2, 7, 2, 3, 6, 1, 6, 6, 3, 1, 9, 5, 9, 6, 4, 
           5, 1, 9, 1])

    >>> w, x, y, z = unflatten(*flatten(a, b, c, d))

    >>> w == a
    True

    >>> np.array_equal(x, b)
    True

    >>> np.array_equal(y, c)
    True

    >>> np.array_equal(z, d)
    True

    """
    ravel = partial(np.ravel, order=order)
    flattened = np.hstack(map(ravel, arys))

    if returns_shapes:
        # TODO: decide whether to return as list, or iterator?
        shapes = list(map(np.shape, arys))
        return flattened, shapes
    
    return flattened

def unflatten(ary, shapes, order='C'):
    """
    Given a flat (1d) array, and a list of shapes (represented as 
    tuples), return a list of ndarrays with the specified shapes.

    Parameters
    ----------
    ary : a 1d array
        A flat (1d) array.
    
    shapes : list of tuples
        A list of ndarray shapes (tuple of array dimensions)

    order : {‘C’, ‘F’, ‘A’}, optional
        Reshape array using index order: C (row-major), Fortran 
        (column-major) order, or preserve the C/Fortran ordering. 
        The default is ‘C’.
    
    Returns
    -------
    list of ndarrays
        A list of ndarrays with the specified shapes.

    See Also
    --------
    pyalacarte.utils.flatten : its inverse

    Notes
    -----
    Equivalent to::

        lambda ary, shapes, order='C': map(partial(custom_reshape, order=order), np.hsplit(ary, np.cumsum(map(partial(np.prod, dtype=int), shapes))), shapes)

    Examples
    --------
    >>> list(unflatten(np.array([4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(2,), (3,), (2, 3)])) # doctest: +NORMALIZE_WHITESPACE
    [array([4, 5]), array([8, 9, 1]), array([[4, 2, 5], [3, 4, 3]])]

    >>> list(unflatten(np.array([7, 4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(), (1,), (4,), (2, 3)])) # doctest: +NORMALIZE_WHITESPACE
    [7, array([4]), array([5, 8, 9, 1]), array([[4, 2, 5], [3, 4, 3]])]

    Fortran-order:

    >>> list(unflatten(np.array([4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(2,), (3,), (2, 3)], order='F')) 
    ... # doctest: +NORMALIZE_WHITESPACE
    [array([4, 5]), array([8, 9, 1]), array([[4, 5, 4], [2, 3, 3]])]

    >>> list(unflatten(np.array([7, 4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(), (1,), (4,), (2, 3)], order='F')) 
    ... # doctest: +NORMALIZE_WHITESPACE
    [7, array([4]), array([5, 8, 9, 1]), array([[4, 5, 4], [2, 3, 3]])]
    
    >>> list(unflatten(np.array([7, 4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(), (1,), (3,), (2, 3)])) 
    ... # doctest: +NORMALIZE_WHITESPACE
    [7, array([4]), array([5, 8, 9]), array([[1, 4, 2], [5, 3, 4]])]

    >>> list(unflatten(np.array([7, 4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    ...     [(), (1,), (5,), (2, 3)])) 
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    ValueError: total size of new array must be unchanged

    np.array([7, 4, 5, 8, 9, 1, 4, 2, 5, 3, 4, 3]), 
    [(), (1,), (4,), (2, 3)]

    """
    # important to make sure dtype is int
    # since prod on empty tuple is a float (1.0)
    sizes = list(map(partial(np.prod, dtype=int), shapes))
    sections = np.cumsum(sizes)
    subarrays = np.hsplit(ary, sections)
    # Subtle but important: last element of subarrays is always a extraneous
    # empty array but is ignored when zipped with shapes. Not really a bug...
    return map(partial(custom_reshape, order=order), subarrays, shapes)

def custom_reshape(a, newshape, order='C'):
    """
    Identical to `numpy.reshape` except in the case where `newshape` is
    the empty tuple, in which case we return a scalar instead of a
    0-dimensional array.
    
    Examples
    --------
    >>> a = np.arange(6)
    >>> np.array_equal(np.reshape(a, (3, 2)), custom_reshape(a, (3, 2)))
    True

    >>> custom_reshape(np.array([3.14]), newshape=())
    3.14

    >>> custom_reshape(np.array([2.71]), newshape=(1,))
    array([ 2.71])
    """
    if newshape == ():
        return np.asscalar(a)
    
    return np.reshape(a, newshape, order)

def map_indices(fn, iterable, indices):
    
    """
    Notes
    -----
    Roughly equivalent to, though more efficient than::

        lambda fn, iterable, *indices: (fn(arg) if i in indices else arg for i, arg in enumerate(iterable))

    Examples
    --------

    >>> a = [4, 6, 7, 1, 6, 8, 2]

    >>> list(map_indices(partial(mul, 3), a, [0, 3, 5]))
    [12, 6, 7, 3, 6, 24, 2]

    >>> b = [9., np.array([5., 6., 2.]), np.array([[5., 6., 2.], [2., 3., 9.]])]
    
    >>> list(map_indices(np.log, b, [0, 2])) # doctest: +NORMALIZE_WHITESPACE
    [2.1972245773362196, 
     array([ 5.,  6.,  2.]), 
     array([[ 1.60943791,  1.79175947,  0.69314718],
            [ 0.69314718,  1.09861229,  2.19722458]])]

    .. todo::

       Floating point precision

    >>> list(map_indices(np.exp, list(map_indices(np.log, b, [0, 2])), [0, 2]))
    ... # doctest: +NORMALIZE_WHITESPACE +SKIP
    [9.,
     array([5., 6., 2.]),
     array([[ 5.,  6.,  2.],
            [ 2.,  3.,  9.]])]
    """

    index_set = set(indices)
    for i, arg in enumerate(iterable):
        if i in index_set:
            yield fn(arg)
        else:
            yield arg

class CatParameters(object):

    def __init__(self, params, log_indices=None):

        self.pshapes = [np.asarray(p).shape if not np.isscalar(p)
                        else 1 for p in params]
        
        if log_indices is not None:
            self.log_indices = log_indices
        else:
            self.log_indices = []

    def flatten(self, params):
        """ This will take a list of parameters of scalars or arrays, and
            return a flattened array which is a concatenation of all of these
            parameters.

            This could be useful for using with an optimiser!

            Arguments:
                params: a list of scalars of arrays.

            Returns:
                list: a list or 1D array of scalars which is a flattened
                    concatenation of params.
        """

        vec = []
        for i, p in enumerate(params):
            fp = np.atleast_1d(p).flatten()
            vec.extend(fp if i not in self.log_indices else np.log(fp))

        return np.array(vec)

    def flatten_grads(self, params, grads):

        vec = []
        for i, (p, g) in enumerate(zip(params, grads)):
            g = np.atleast_1d(g)

            # Chain rule if log params used
            if i in self.log_indices:
                g *= np.atleast_1d(p)

            vec.extend(g.flatten())

        return np.array(vec)

    def unflatten(self, flatparams):
        """ This will turn a flattened list of parameters into the original
            parameter argument list, given a template.

            This could be useful for using after an optimiser!

            Argument:
                params: the template list of parameters.

                flatlist: the flattened list of parameters to turn into the
                    original parameter list.

            Returns:
                list: A list of the same form as params, but with the values
                    from flatlist.
        """

        rparams = []
        listind = 0
        for i, p in enumerate(self.pshapes):
            if np.isscalar(p):
                up = flatparams[listind]
                listind += 1
            else:
                nelems = np.product(p)
                up = np.reshape(flatparams[listind:(listind + nelems)], p)
                listind += nelems

            rparams.append(up if i not in self.log_indices else np.exp(up))

        return rparams

def params_to_list(params):
    """ This will take a list of parameters of scalars or arrays, and return a
        flattened array which is a concatenation of all of these parameters.

        This could be useful for using with an optimiser!

        Arguments:
            params: a list of scalars of arrays.

        Returns:
            list: a list or 1D array of scalars which is a flattened
                concatenation of params.
    """

    vec = []
    for p in params:
        vec.extend(np.atleast_1d(p).flatten())

    return vec


def list_to_params(params, flatlist):
    """ This will turn a flattened list of parameters into the original
        parameter argument list, given a template.

        This could be useful for using after an optimiser!

        Argument:
            params: the template list of parameters.

            flatlist: the flattened list of parameters to turn into the
                original parameter list.

        Returns:
            list: A list of the same form as params, but with the values from
                flatlist.
    """

    rparams = []
    listind = 0
    for p in params:
        if np.isscalar(p):
            rparams.append(flatlist[listind])
            listind += 1
        else:
            p = np.asarray(p)
            nelems = np.product(p.shape)
            rparams.append(np.reshape(flatlist[listind:(listind + nelems)],
                                      p.shape))
            listind += nelems

    return rparams
