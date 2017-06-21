from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_csv


setup(
    name='unsync_csv',
    description='CSV related commands for the Unsync tool.',
    version=unsync_csv.__version__,
    package_dir={'unsync_csv': 'unsync_csv'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'petl',
    ],
)
