#!/usr/bin/env python

from distutils.core import setup

setup(name='eupy',
      version='0.0.1',
      description='Python set of utils and libraries',
      url='http://github.com/fivosts/eupy',
      author='Foivos Tsimpourlas',
      author_email='fivos_ts@hotmail.com',
      license='MIT',
      package_dir = {'': 'eupy'},
      packages=['mrcrawley', 'native'],
      py_modules = ['hermes/hermes.py'],
      install_requires=[
          'scrapy',
          'logging'#,
          # 'lazytools'
      ],
      zip_safe=True)
