from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_google


setup(
    name='unsync_google',
    description='Commands to access the Google APIs using the Unsync Tool.',
    version=unsync_google.__version__,
    package_dir={'unsync_google': 'unsync_google'},
    packages=find_packages(),
    install_requires=[
        'unsync',
    ],
)
