from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_fs


setup(
    name='unsync_fs',
    description='Commands for the Unsync tool to work with the filesystem.',
    version=unsync_fs.__version__,
    package_dir={'unsync_fs': 'unsync_fs'},
    packages=find_packages(),
    # package_data={
    #     'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    # },
    # include_package_data=True,
    install_requires=[
        'unsync',
        'fs'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'unsync=unsync.command:cli',
    #     ]
    # }
)
