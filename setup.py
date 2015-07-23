# -*- coding: utf-8 -*-
"""\
===================
text_based_switcher
===================

Text-based window switcher for Unity
"""

from setuptools import setup, find_packages
import os, sys

version = '0.0.2.dev0'

this_directory = os.path.abspath(os.path.dirname(__file__))

def read(*names):
    return open(os.path.join(this_directory, *names), 'r').read().strip()

long_description = '\n\n'.join(
    [read(*paths) for paths in (('README.rst',),('CHANGES.rst',))]
    )
dev_require = []
if sys.version_info < (2, 7):
    dev_require += ['unittest2']


setup(
    name='text-based-switcher',
    version=version,
    description="Text-based window switcher for Unity",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Environment :: X11 Applications",
        "Environment :: Plugins",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment :: Window Managers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        ],
    keywords='ubuntu unity switcher',
    author='Jean Jordaan',
    author_email='jean.jordaan@gmail.com',
    url='http://pypi.python.org/pypi/text-based-switcher',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # 3rd party
        'setuptools'
        # wmctrl or ruamel.ewmh
        # Others
        ],
    entry_points={
        'console_scripts': ['list_windows=text_based_switcher.__main__:main']
        },
    tests_require=dev_require,
    test_suite='tests.all_tests',
    extras_require={
        'dev': dev_require
    })
