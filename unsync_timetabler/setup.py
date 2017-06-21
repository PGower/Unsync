from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_timetabler


setup(
    name='unsync_timetabler',
    description='Commands for the Unsync tool to work with Timetabler source files (ptf9, dof9).',
    version=unsync_timetabler.__version__,
    package_dir={'unsync_timetabler': 'unsync_timetabler'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'lxml',
        'petl'
    ],
)
