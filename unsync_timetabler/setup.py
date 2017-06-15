from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_timetabler


setup(
    name='unsync_timetabler',
    description='Commands for the Unsync tool to work with Timetabler source files (ptf9, dof9).',
    version=unsync_timetabler.__version__,
    package_dir={'unsync_timetabler': 'unsync_timetabler'},
    packages=find_packages(),
    # package_data={
    #     'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    # },
    # include_package_data=True,
    install_requires=[
        'unsync',
        'lxml'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'unsync=unsync.command:cli',
    #     ]
    # }
)
