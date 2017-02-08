from setuptools import setup, find_packages
import os

# BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# PACKAGES = find_packages(os.path.join(BASE_PATH, 'unsync'))

# print PACKAGES

setup(
    name='CanvasUnsync',
    description='A tool for manipulating data, uses the PETL library in the background. Originally designed to help synchronize Instructure Canvas enrollment data from a variety of school sources.',
    version='0.1',
    package_dir={'unsync': 'unsync'},
    packages=find_packages(),
    package_data={
        'templates': ['unsync/templates/*.*', 'unsync/templates/*'],
    },
    include_package_data=True,
    install_requires=[
        'arrow==0.8.0',
        'backports.shutil-get-terminal-size==1.0.0',
        'click==6.6',
        'colorama==0.3.7',
        'decorator==4.0.10',
        'enum34==1.1.6',
        'ipython==5.1.0',
        'ipython-genutils==0.1.0',
        'Jinja2==2.8',
        'ldap3==1.4.0',
        'MarkupSafe==0.23',
        'pathlib2==2.1.0',
        'petl==1.0.11',
        'petname==2.0',
        'pickleshare==0.7.4',
        'prompt-toolkit==1.0.9',
        'pyasn1==0.1.9',
        'Pygments==2.1.3',
        'python-dateutil==2.5.3',
        'PyYAML==3.12',
        'requests==2.11.1',
        'simplegeneric==0.8.1',
        'six==1.10.0',
        'traitlets==4.3.1',
        'wcwidth==0.1.7',
        'win-unicode-console==0.5',
        'pycanvas',
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'unsync=unsync.command:cli',
        ]
    }
)
