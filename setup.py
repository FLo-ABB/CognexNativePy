from setuptools import setup, find_packages

setup(
    name='CognexNativePy',
    version='1.0.0',
    description='A Python library for communicating with Cognex In-Sight vision systems. Wrapper of the native commands',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Florian LOBERT',
    url='https://github.com/FLo-ABB/CognexNativePy',
    packages=find_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
)
