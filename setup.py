#!/usr/bin/env python

from distutils.core import setup
import dougrain

base_url = "http://github.com/wharris/dougrain/"

setup(
    name = 'dougrain',
    version = dougrain.__version__,
    description = 'HAL JSON parser and generator',
    author = 'Will Harris',
    author_email = 'will@greatlibrary.net',
    url = base_url,
    packages = ['dougrain'],
    provides = ['dougrain'],
    long_description=open("README.md").read(),
    install_requires = ['uritemplate >= 0.5.1'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD Licencse',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)


