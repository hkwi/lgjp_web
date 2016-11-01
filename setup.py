import sys
from setuptools import setup, find_packages

setup(name='lgjp_web',
	version='0.1.0',
	description='Japan local goverment URL RDF generator',
	long_description=open("README.rst").read(),
	author='Hiroaki Kawai',
	author_email='hiroaki.kawai@gmail.com',
	url='https://github.com/hkwi/lgjp_web/',
	packages=find_packages(),
)
