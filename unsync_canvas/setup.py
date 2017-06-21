from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_canvas

setup(
    name='unsync_canvas',
    description='Canvas LMS API commands for the Unsync Tool.',
    version=unsync_canvas.__version__,
    package_dir={'unsync_canvas': 'unsync_canvas'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'pycanvas',
    ],
)
