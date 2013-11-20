#!/usr/bin/env python

from setuptools import setup

long_description = open('README.md', 'r').read()

setup(
    name="glass",
    version="0.1",
    packages=[
        "glass"
    ],
    author="Paul Tagliamonte",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='does some stuff with things & stuff',
    license="Expat",
    url="",
    platforms=['any']
)
