from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_petl


setup(
    name='Unsync PETL',
    description='PETL Library commands for the Unsync Tool.',
    version=unsync_petl.__version__,
    package_dir={'unsync_petl': 'unsync_petl'},
    packages=find_packages(),
    # package_data={
    #     'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    # },
    # include_package_data=True,
    install_requires=[
        'unsync',
        'petl',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'unsync=unsync.command:cli',
    #     ]
    # }
)
