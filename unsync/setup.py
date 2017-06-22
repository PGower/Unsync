from setuptools import setup, find_packages

import unsync

setup(
    name='unsync',
    description='A general purpose tool for manipulating data streams using scripts. Internally uses the PETL library to store and manipulate data.',
    version=unsync.__version__,
    package_dir={'unsync': 'unsync'},
    packages=find_packages(),
    package_data={
        'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    },
    include_package_data=True,
    install_requires=[
        'click==6.7',
        'colorama',
        'ipython',
        'petl',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'unsync=unsync.cli:cli',
        ]
    }
)
