#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='chevron',
      version='0.7',
      license='MIT',
      description='Mustache templating language renderer',
      author='noah morrison',
      author_email='noah@morrison.ph',
      url='',
      download_url='/tarball/0.7',
      packages=['chevron'],
      entry_points={
          'console_scripts': ['chevron=chevron:cli_main']
      },
      classifiers=[
          'Development Status :: 4 - Beta',

          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',

          'Topic :: Text Processing :: Markup'
      ]
      )
