#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
os.listdir

setup(
   name='s9700_53dx',
   version='1.0',
   description='Module to initialize UfiSpace S9700-53DX platforms',
   packages=find_packages(),
   install_requires=['smbus-cffi', 'portio']
)

