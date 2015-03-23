try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'XSLT migration of SAIT assessment questions',
    'author': 'Todd Saskiw',
    'url': 'Project URL',
    'download_url': 'Download URL',
    'authot_email': 'todd.saskiw@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['d2l_migrator'],
    'scripts': [],
    'name': 'D2L Migrator'
}

setup(**config)
