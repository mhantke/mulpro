#!/usr/bin/env python
        
from setuptools import setup, find_packages

setup(name='mulpro',
      version='0.1.6',
      description='Running any worker function in parallel and producing output in a separate process',
      author='Max F. Hantke',
      author_email='maxhantke@gmail.com',
      url='https://github.com/mhantke/mulpro',
      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.2',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
      ],
      keywords='multiprocessing pipes parallel processes',
      #install_requires=['numpy', 'multiprocessing', 'h5py', 'mpi4py>=2.0.0'],
      packages = ['mulpro'],
)   
    
