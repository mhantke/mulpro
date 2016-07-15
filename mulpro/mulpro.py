#================================#
# MulPro                         #
#================================# 
#
# Author: Max Hantke
# Email: maxhantke@gmail.com

import numpy as np
import multiprocessing
import time

import logging
logger = logging.getLogger(__name__)

import log
from log import log_debug, log_info, log_warning, log_and_raise_error

WARNING_AFTER_JOB_DURATION_SEC = 30

import traceback, sys

def _worker_call(worker,pipe):
    try:
        work_package = pipe.recv()
        while work_package is not None:
            t = time.time()
            result = worker(work_package)
            result["_time"] = time.time() - t
            pipe.send(result)
            work_package = pipe.recv()
    except:
        # Put all exception text into an exception and raise that
        raise Exception("".join(traceback.format_exception(*sys.exc_info())))
    
def mulpro(Nprocesses, worker, getwork, logres=None):
    multiprocessing.log_to_stderr(logger.getEffectiveLevel())
    pipes_end_host = list(np.zeros(Nprocesses))
    pipes_end_worker = list(np.zeros(Nprocesses))
    processes = list(np.zeros(Nprocesses))
    processes_job_sent = np.zeros(Nprocesses, dtype=np.bool)
    processes_job_time = np.zeros(Nprocesses, dtype=np.float)

    for i in range(Nprocesses):
        pipes_end_host[i], pipes_end_worker[i] =  multiprocessing.Pipe()
        processes[i] = multiprocessing.Process(target=_worker_call,
                                               args=(worker,pipes_end_worker[i],) )
        processes[i].start()
        log_debug(logger, "Process %i started" % i)

    end = False

    N_done = 0

    t_start = time.time()
    
    # Send out initial jobs
    for i in range(Nprocesses):
        work_package = getwork()
        if work_package is not None:
            pipes_end_host[i].send(work_package)
            processes_job_sent[i] = True
            processes_job_time[i] = time.time()
            log_debug(logger, "Initial job for process %i sent" % i)
        else:
            end = True
            break

    err = False
    
    while not (end and not processes_job_sent.any()) and not err:
        if end:
            log_debug(logger, "Waiting for processes %s to finish" % str(np.arange(Nprocesses)[processes_job_sent]))

        i_processes = range(Nprocesses)
        for i in i_processes:
            waiting_counter = 0
            while not processes[i].is_alive():
                time.sleep(5)
                log_debug(logger, "Process %i: Cannot reach process" % (i))
                waiting_counter += 5
                if waiting_counter > 60:
                    log_and_raise_error(logger, "Process %i died!" % i)
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
                    log_info(logger, "Datarate %.1f Hz; job %i; process %i/%i; work %.2f sec / logging %.2f sec" % (N_done/(time.time()-t_start),N_done,i,Nprocesses,result["_time"],t_log))
                    if not end:
                        work_package = getwork()
                        if work_package is None:
                            end = True
                        else:
                            pipes_end_host[i].send(work_package)
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

