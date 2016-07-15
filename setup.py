#!/usr/bin/env python

from warnings import warn

try:
    import multiprocessing
    multiprocessing_av = True
except ImportError:
    multiprocessing_av = False
        
if multiprocessing_av:
        
    from setuptools import setup

    setup(name='h5writer',
          version='0.1.0',
          description='Running any worker function in parallel and producing output in a separate process',
          author='Max F. Hantke',
          author_email='maxhantke@gmail.com',
          url='https://github.com/mhantke/mulpro',
          #install_requires=['numpy', 'h5py', 'mpi4py>=2.0.0'],
          packages = ['mulpro'],
          #package_dir={'h5writer':'src'},
    )   
    
else:
    
    print 100*"*"

    print "\tThe multiprocessing package cannot be imported! Please install multiprocessing."

    print 100*"*"

