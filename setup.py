# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='jarhead',
    version='0.0.1',
    description="Jarhead is Alokin's common codebase",
    long_description=readme,
    author='Alokin Software Pvt Ltd',
    author_email='hello@alokin.in',
    url='http://www.alokin.in',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

