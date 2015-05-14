from __future__ import absolute_import

import numpy as np
import os
import shutil
import pickle

from partd.numpy import Numpy

def test_numpy():
    dt = np.dtype([('a', 'i4'), ('b', 'i2'), ('c', 'f8')])
    with Numpy('foo') as p:
        p.append({'a': np.array([10, 20, 30], dtype=dt['a']),
                  'b': np.array([ 1,  2,  3], dtype=dt['b']),
                  'c': np.array([.1, .2, .3], dtype=dt['c'])})
        p.append({'a': np.array([70, 80, 90], dtype=dt['a']),
                  'b': np.array([ 7,  8,  9], dtype=dt['b']),
                  'c': np.array([.7, .8, .9], dtype=dt['c'])})

        result = p.get(['a', 'c'])
        assert (result[0] == np.array([10, 20, 30, 70, 80, 90],dtype=dt['a'])).all()
        assert (result[1] == np.array([.1, .2, .3, .7, .8, .9],dtype=dt['c'])).all()

        with p.lock:  # uh oh, possible deadlock
            result = p.get(['a'], lock=False)


def test_nested():
    with Numpy('foo') as p:
        p.append({'x': np.array([1, 2, 3]),
                 ('y', 1): np.array([4, 5, 6]),
                 ('z', 'a', 3): np.array([.1, .2, .3])})
        assert (p.get(('z', 'a', 3)) == np.array([.1, .2, .3])).all()


def test_serialization():
    with Numpy('foo') as p:
        p.append({'x': np.array([1, 2, 3])})
        q = pickle.loads(pickle.dumps(p))
        assert (q.get('x') == [1, 2, 3]).all()


def test_object_dtype():
    x = np.array(['Alice', 'Bob', 'Charlie'], dtype='O')
    with Numpy('foo') as p:
        p.append({'x': x})
        p.append({'x': x})
        assert (p.get('x') == np.concatenate([x, x])).all()
