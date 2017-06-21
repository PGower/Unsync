from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_petl


setup(
    name='unsync_petl',
    description='PETL Library commands for the Unsync Tool.',
    version=unsync_petl.__version__,
    package_dir={'unsync_petl': 'unsync_petl'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'petl',
    ],
)
