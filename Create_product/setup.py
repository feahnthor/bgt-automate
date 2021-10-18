"""
Installs packages needed for this program to run on users computer. Done through python installer *pip*

To install: python setup.py install
To build: python setup.py.build
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name = 'Infigo_Automation',
    Version = '1.0.0',
    description = 'Automation for backgroundtown',
    author = 'feahnthor',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'infigo, automation',
    packages = find_packages(include=['helium', 'asana', 'python-json-logger', 'numpy']), # necessary for this program to run at all
    install_requires = ['helium', 'asana', 'python-json-logger', 'numpy'],
    python_requires = '>=2.7'
    )