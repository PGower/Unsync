from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_pytds


setup(
    name='unsync_pytds',
    description='PETL Library commands for the Unsync Tool.',
    version=unsync_pytds.__version__,
    package_dir={'unsync_pytds': 'unsync_pytds'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'python-tds',
    ],
)
