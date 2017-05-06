#================================#
# MulPro                         #
#================================# 
#
# Author: Max Hantke
# Email: maxhantke@gmail.com

import os
import numpy as np
import multiprocessing
import time

import logging
logger = logging.getLogger(__name__)

import log
from log import log_debug, log_info, log_warning, log_and_raise_error

WARNING_AFTER_JOB_DURATION_SEC = 30

import traceback, sys


import traceback
run_old = multiprocessing.Process.run

def run_new(*args, **kwargs):
    try:
        run_old(*args, **kwargs)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        traceback.print_exc(file=sys.stdout)

multiprocessing.Process.run = run_new

def _worker_call(worker, pipe):
    pid = os.getpid()
    log_debug(logger, "Worker process started successfully! (PID: %i)" % pid)
    log_debug(logger, "Waiting to receive work package... (PID: %i)" % pid)
    work_package = pipe.recv()
    while work_package is not None:
        log_debug(logger, "Work package received! (PID: %i)" % pid)
        t = time.time()
        result = worker(work_package)
        result["_time"] = time.time() - t
        log_debug(logger, "Sending out result... (PID: %i)" % pid)
        pipe.send(result)
        log_debug(logger, "Waiting to receive work package... (PID: %i)" % pid)
        work_package = pipe.recv()
    #except:
        # Put all exception text into an exception and raise that
     #   raise Exception("".join(traceback.format_exception(*sys.exc_info())))
    log_debug(logger, "Reached end of worker call function")
    
def mulpro(Nprocesses, worker, getwork, logres=None):
    multiprocessing.log_to_stderr(logger.getEffectiveLevel())
    pipes_end_host = list(np.zeros(Nprocesses))
    pipes_end_worker = list(np.zeros(Nprocesses))
    processes = list(np.zeros(Nprocesses))
    processes_job_sent = np.zeros(Nprocesses, dtype=np.bool)
    processes_job_time = np.zeros(Nprocesses, dtype=np.float)
    iprocesses = range(Nprocesses)
    
    for i in iprocesses:
        pipes_end_host[i], pipes_end_worker[i] =  multiprocessing.Pipe()
        processes[i] = multiprocessing.Process(target=_worker_call,
                                               args=(worker, pipes_end_worker[i]) )
        processes[i].start()
        log_debug(logger, "Process %i started" % i)

    #for i in iprocesses:
    #    print i, processes[i].is_alive()
        
    end = False

    N_done = 0

    t_start = time.time()

    work_packages = list(np.zeros(Nprocesses))
    
    # Send out initial jobs
    for i in iprocesses:
        work_packages[i] = getwork()
        if work_packages[i] is not None:
            pipes_end_host[i].send(work_packages[i])
            processes_job_sent[i] = True
            processes_job_time[i] = time.time()
            log_debug(logger, "Initial job for process %i sent" % i)
        else:
            end = True
            break

    err = False
    
    while not (end and not processes_job_sent.any()) and not err:
        if end:
            log_debug(logger, "Waiting for processes %s to finish" % str(np.asarray(iprocesses)[processes_job_sent]))

        for i in iprocesses:
            if not processes[i].is_alive():
                log_and_raise_error(logger, "Process %i has died with exitcode %i." % (i, processes[i].exitcode))
                
            job_sent = processes_job_sent[i]
            job_duration = time.time()-processes_job_time[i]
            log_debug(logger, "Process %i: job sent = %i (%f sec ago)" % (i,job_sent,job_duration))
            if job_sent:
                log_debug(logger, "Polling process %i" % i)
                if pipes_end_host[i].poll():
                    result = pipes_end_host[i].recv()
                    processes_job_sent[i] = False
                    N_done += 1
                    t_log = time.time()
                    if logres != None:
                        logres(result)
                    t_log = time.time() - t_log
                    log_info(logger, "Datarate %.1f Hz; job %i; process %i/%i; work %.2f sec / logging %.2f sec" % (N_done/(time.time()-t_start), N_done, i,
                                                                                                                    Nprocesses, result["_time"], t_log))
                    if not end:
                        work_packages[i] = getwork()
                        if work_packages[i] is None:
                            end = True
                        else:
                            pipes_end_host[i].send(work_packages[i])
                            processes_job_sent[i] = True
                            processes_job_time[i] = time.time()
                    else:
                        continue
                else:
                    if job_duration > WARNING_AFTER_JOB_DURATION_SEC:
                        log_warning(logger, "Process %i has not returned from work call for %s sec" % (i,job_duration))
                        #if job_duration > 100:
                        #    log_warning(logger, "Process %i has not returned from work call for more than 1000 sec. Abort." % (i))
                        #    err = True
                        #    break


        time.sleep(0.01)

    for i in range(Nprocesses):
        pipes_end_host[i].send(None)
        processes[i].join(10)
        pipes_end_host[i].close()

