#!/usr/bin/python

from distutils.core import setup

setup(name='chevron',
      version='0.1',
      license='MIT',
      description='Mustache templating language renderer',
      author='noah morrison',
      author_email='noah@morrison.ph',
      url='https://github.com/noahmorrison/chevron',
      packages=['chevron'],
      entry_points={
          'console_scripts': ['chevron=chevron:cli_main']
      }
      )
