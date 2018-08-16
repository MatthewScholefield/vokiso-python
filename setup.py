#!/usr/bin/env python3
from setuptools import setup

setup(
    name='vokiso',
    version='0.1.0',
    description='Voice chat for the workplace done right',
    url='http://github.com/MatthewScholefield/vokiso',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    packages=[
        'vokiso'
    ],
    install_requires=[
        'py2p',
        'pyaudio',
        'numpy',
        'sonopy',
        'miniupnpc',
        'ipgetter',
        'PyAL',
        'pygame'
    ],
    entry_points={
        'console_scripts': [
            'vokiso = vokiso.__main__:main'
        ]
    }
)
