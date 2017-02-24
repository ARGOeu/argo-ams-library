from distutils.core import setup
import glob

NAME='argo-ams-library'

def get_ver():
    try:
        with open(NAME+'.spec') as f:
            for line in f:
                if "Version:" in line:
                    return line.split()[1]
    except IOError:
        print "Make sure that %s is in directory"  % (NAME+'.spec')
        raise SystemExit(1)

setup(
    name = NAME,
    version = get_ver(),
    author = 'SRCE',
    author_email = 'dvrcic@srce.hr',
    license = 'ASL 2.0',
    description = 'A simple python library for interacting with the ARGO Messaging Service',
    long_description = 'A simple python library for interacting with the ARGO Messaging Service',
    url = 'https://github.com/ARGOeu/argo-nagios-ams-publisher',
    package_dir = {'argo_ams_library': 'pymod/'},
    packages = ['argo_ams_library'],
    )
