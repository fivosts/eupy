from setuptools import setup

setup(name='mrcrawley',
      version='0.0.1',
      description='Python utility to scrap data from websites',
      url='http://github.com/fivosts/MrCrawley',
      author='Foivos Tsimpourlas',
      author_email='fivos_ts@hotmail.com',
      license='MIT',
      packages=['mrcrawley'],
      install_requires=[
          'scrapy',
          'logging'#,
          # 'lazytools'
      ],
      zip_safe=True)
