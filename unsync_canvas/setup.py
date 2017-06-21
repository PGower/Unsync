from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_canvas

# BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# PACKAGES = find_packages(os.path.join(BASE_PATH, 'unsync'))

# print PACKAGES

setup(
    name='unsync_canvas',
    description='Canvas LMS API commands for the Unsync Tool.',
    version=unsync_canvas.__version__,
    package_dir={'unsync_canvas': 'unsync_canvas'},
    packages=find_packages(),
    # package_data={
    #     'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    # },
    # include_package_data=True,
    install_requires=[
        'unsync',
        'pycanvas',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'unsync=unsync.command:cli',
    #     ]
    # }
)
