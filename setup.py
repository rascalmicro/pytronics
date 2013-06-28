#!/usr/bin/env python

from distutils.core import setup

setup(name='pytronics',
    version='0.4.2',
    license='GPLv3',
    py_modules=['i2c', 'pytronics'],
    description='Rascal hardware API',
    long_description='Hardware control library for the Rascal, a small computer for art and science',
    author='Brandon Stafford',
    author_email='brandon@rascalmicro.com',
    url='http://rascalmicro.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python'
        ],
    )
