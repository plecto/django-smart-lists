#!/usr/bin/env python
import os
from setuptools import find_packages, setup
from smart_lists import version


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-smart-lists',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Easy lists for django views',
    long_description='See README.md',
    url='https://github.com/plecto/django-smart-lists',
    author='Kristian Oellegaard',
    author_email='kristian@kristian.io',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
