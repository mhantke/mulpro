#!/usr/bin/env python
import numpy as np
import time
from mulpro import mulpro

counter = 0
n_tasks = 50

def my_worker(work_package):
    res = {
        "A": work_package["A"],
        "B": work_package["B"],
        "A+B": 10**(work_package["A"]+work_package["B"]),
    }
    time.sleep(np.random.rand()*2)
    return res

def my_getwork():
    global counter
    if counter < n_tasks:
        counter += 1
        #np.random.seed()
        work_package = {
            "A": np.random.rand(1000,1000),
            "B": np.random.rand(1000,1000),
        }
        return work_package 
    else:
        return None

def my_logres(res):
    print res["A"][0,0], res["B"][0,0], res["A+B"][0,0]

mulpro(Nprocesses=4, worker=my_worker, getwork=my_getwork, logres=my_logres)
