from __future__ import absolute_import

from setuptools import setup, find_packages
import unsync_ldap3


setup(
    name='unsync_ldap3',
    description='LDAP related commands for the Unsync tool.',
    version=unsync_ldap3.__version__,
    package_dir={'unsync_ldap3': 'unsync_ldap3'},
    packages=find_packages(),
    install_requires=[
        'unsync',
        'ldap3',
    ],
)
