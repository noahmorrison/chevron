#!/usr/bin/env python

import chevron.metadata

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rest')
except (ImportError, RuntimeError):
    print('\n\n!!!\npypandoc not loaded\n!!!\n')
    readme = ''



setup(name='chevron',
      version=chevron.metadata.version,
      license='MIT',

      description='Mustache templating language renderer',
      long_description=readme,

      author='noah morrison',
      author_email='noah@morrison.ph',
      url='https://github.com/noahmorrison/chevron',

      packages=['chevron'],
      entry_points={
          'console_scripts': ['chevron=chevron:cli_main']
      },
      install_requires=[
          'python-frontmatter'
      ],

      classifiers=[
          'Development Status :: 4 - Beta',

          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing :: Markup'
      ]
      )
