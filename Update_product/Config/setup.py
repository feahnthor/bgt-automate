"""
Installs packages needed for this program to run on users computer. Done through python installer *pip*

To install: python setup.py install
To build: python setup.py.build
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name = 'Update Products',
    Version = '1.0.0',
    description = 'Update existing products for backgroundtown',
    author = 'feahnthor',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'infigo, automation, update',
    packages = find_packages(include=['PySide6','python-json-logger']), # necessary for this program to run at all
    install_requires = ['PySide6', 'python-json-logger'],
    python_requires = '>=3.6'
    )