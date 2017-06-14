from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_ldap3

# BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# PACKAGES = find_packages(os.path.join(BASE_PATH, 'unsync'))

# print PACKAGES

setup(
    name='Unsync Ldap3',
    description='LDAP related commands for the Unsync tool.',
    version=unsync_ldap3.__version__,
    package_dir={'unsync_ldap3': 'unsync_ldap3'},
    packages=find_packages(),
    # package_data={
    #     'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    # },
    # include_package_data=True,
    install_requires=[
        'unsync',
        'ldap3',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'unsync=unsync.command:cli',
    #     ]
    # }
)
