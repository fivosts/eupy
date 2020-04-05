#!/usr/bin/env python

from distutils.core import setup

setup(name='eupy',
      version='0.0.1',
      description='Python set of utils and libraries',
      url='http://github.com/fivosts/eupy',
      author='Foivos Tsimpourlas',
      author_email='fivos_ts@hotmail.com',
      license='MIT',
      package_dir = {'hermes'   : 'eupy/hermes',
                     'mrcrawley': 'eupy/mrcrawley',
                     'native'   : 'eupy/native',
                    },
      packages=['mrcrawley', 'native', 'hermes'],
      )
