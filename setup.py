from setuptools import setup
from os import path
import sys

NAME = 'argo-ams-library'

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


def get_ver():
    try:
        with open(NAME + '.spec') as f:
            for line in f:
                if "Version:" in line:
                    return line.split()[1]
    except IOError:
        print("Make sure that %s is in directory" % (NAME + '.spec'))
        raise SystemExit(1)


REQUIREMENTS = []
if sys.version_info[0] == 2:
    REQUIREMENTS = ['requests==2.20.0'],
else:
    REQUIREMENTS = ['requests'],

setup(
    name=NAME,
    version=get_ver(),
    author='SRCE, GRNET',
    author_email='dvrcic@srce.hr, agelos.tsal@gmail.com, kaggis@gmail.com, themiszamani@gmail.com',
    license='ASL 2.0',
    description='A simple python library for interacting with the ARGO Messaging Service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    tests_require=[
        'setuptools_scm',
        'httmock',
        'pytest'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    url='https://github.com/ARGOeu/argo-ams-library',
    package_dir={'argo_ams_library': 'pymod/'},
    packages=['argo_ams_library'],
    install_requires=REQUIREMENTS
)
