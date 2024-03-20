from setuptools import setup, find_packages

setup(
    name='pycognex',
    version='0.1.0',
    description='A Python library for communicating with Cognex In-Sight vision systems. Wrapper of the native commands',
    author='Florian LOBERT',
    url='https://github.com/FLo-ABB/pycognex',
    packages=find_packages(where='src'),
    package_dir={'': 'src/pycognex'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
)
