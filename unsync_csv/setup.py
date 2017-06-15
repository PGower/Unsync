from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_csv

# BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# PACKAGES = find_packages(os.path.join(BASE_PATH, 'unsync'))

# print PACKAGES

setup(
    name='unsync_csv',
    description='CSV related commands for the Unsync tool.',
    version=unsync_csv.__version__,
    package_dir={'unsync_csv': 'unsync_csv'},
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
