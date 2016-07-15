#!/usr/bin/env python
import numpy as np
from mulpro import mulpro

counter = 0
n_tasks = 50

def my_worker(work_package):
    res = {
        "A": work_package["A"],
        "B": work_package["B"],
        "A+B": work_package["A"]+work_package["B"],
    }
    return res

def my_getwork():
    global counter
    if counter < n_tasks:
        counter += 1
        np.random.seed()
        work_package = {
            "A": np.random.randint(10),
            "B": np.random.randint(10),
        }
        return work_package 
    else: return None

def my_logres(res):
    print res
    
mulpro(Nprocesses=4, worker=my_worker, getwork=my_getwork, logres=my_logres)
