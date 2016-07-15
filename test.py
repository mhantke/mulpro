#!/usr/bin/env python
import numpy as np
from mulpro import mulpro

def my_worker(pipe):
    seed()
    A = np.random.randint(10)
    B = np.random.randint(10)
    res =  "%i+%i=%i" % (A,B,A+B)
    print res
    return res

def my_getwork():
    return np.random.randint(10),np.random.randint(10)

mulpro(Nprocesses=4, worker=my_worker, getwork=my_getwork, logres=None)
