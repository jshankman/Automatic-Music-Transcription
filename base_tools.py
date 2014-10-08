
#-----------------------------------------------
#base_tools.py - basic utils, for the Python Guitar Tuner
#Copyright (c) 2007, Imri Goldberg
#All rights reserved.
#
#Redistribution and use in source and binary forms,
#with or without modification, are permitted provided
#that the following conditions are met:
#
#    * Redistributions of source code must retain the
#       above copyright notice, this list of conditions
#       and the following disclaimer.
#    * Redistributions in binary form must reproduce the
#       above copyright notice, this list of conditions
#       and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#    * Neither the name of the Algorithm.co.il nor the names of
#       its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-----------------------------------------------


import numpy
import bisect
import random

def arg_max(l):
    best = 0
    best_val = l[0]
    for i in xrange(1,len(l)):
        if l[i]>best_val:
            best_val = l[i]
            best = i
    return best

def arg_min(l):
    best = 0
    best_val = l[0]
    for i in xrange(1,len(l)):
        if l[i]<best_val:
            best_val=l[i]
            best = i
    return best

def find_n_biggest(l,n):
    result = [(min(l),-1)]*n
    for i,elem in enumerate(l):
        if elem>=result[0][0]:
            result[0] = elem,i
            def comp(x,y):
                if x<y:
                    return -1
                if x==y:
                    return 0
                return 1
            result.sort(comp)
    return result

def random_select(items, probs):
    probs = numpy.cumsum(probs)
    return items[bisect.bisect(probs, random.random())]

def random_select_dict(d):
    items = d.items()
    keys = [x[0] for x in items]
    values = [x[1] for x in items]
    return random_select(keys, values)

class xxrange(object):
    """A pure-python implementation of xrange.
    Can handle float/long start/stop/step arguments and slice indexing
    """
    #Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/521885

    __slots__ = ['_slice']
    def __init__(self, *args):
        self._slice = slice(*args)
        if self._slice.stop is None:
            # slice(*args) will never put None in stop unless it was
            # given as None explicitly.
            raise TypeError("xrange stop must not be None")

    @property
    def start(self):
        if self._slice.start is not None:
            return self._slice.start
        return 0
    @property
    def stop(self):
        return self._slice.stop
    @property
    def step(self):
        if self._slice.step is not None:
            return self._slice.step
        return 1

    def __hash__(self):
        return hash(self._slice)

    def __cmp__(self, other):
        return (cmp(type(self), type(other)) or
                cmp(self._slice, other._slice))

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.start, self.stop, self.step)

    def __len__(self):
        return self._len()

    def _len(self):
        return max(0, int((self.stop - self.start) / self.step))

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._len())
            return xrange(self._index(start),
                          self._index(stop), step*self.step)
        elif isinstance(index, (int, long)):
            if index < 0:
                fixed_index = index + self._len()
            else:
                fixed_index = index

            if not 0 <= fixed_index < self._len():
                raise IndexError("Index %d out of %r" % (index, self))

            return self._index(fixed_index)
        else:
            raise TypeError("xrange indices must be slices or integers")

    def _index(self, i):
        return self.start + self.step * i
