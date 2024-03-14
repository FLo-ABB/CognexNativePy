# 📷 🐍 NativeCognexPythonWrapper 🐍 📷

WORK IN PROGRESS

VERSION 0.1.0

NativeCognexPythonWrapper is a Python wrapper for the Cognex native mode commands. It provides a simple and intuitive wrapper to interact with Cognex cameras. It's based on the Cognex native mode commands, which can be found in [Cognex Documentation Website](https://support.cognex.com/docs/is_590/web/EN/ise/Content/Communications_Reference/LoadFile.htm?tocpath=Communications%20Reference%7CNative%20Mode%20Communications%7CBasic%20Native%20Mode%20Commands%7CFile%20%26%20Job%20Commands%7C_____1).

## Table of Contents 📜

- [📷 🐍 NativeCognexPythonWrapper 🐍 📷](#--nativecognexpythonwrapper--)
  - [Table of Contents 📜](#table-of-contents-)
  - [Installation 🚀](#installation-)
  - [Usage 📚](#usage-)
  - [Contributing 🤝](#contributing-)
  - [License 📝](#license-)

## Installation 🚀

Download the repository and import the src folder into your project. The wrapper is divided into two main modules: `utils` and `commands`. The `utils` module contains the low-level functions to open and close a socket, and to log into the Cognex camera. The `commands` module contains the high-level functions to interact with the camera, such as loading a file, setting the camera online, and getting the current online status. Look over the `sandbox.py` file to see how to use the wrapper.

## Usage 📚

Example of how to use the wrapper:
```python
from utils import open_socket, close_socket, log_cognex
from commands.file_and_job import load_file, get_file
from commands.execution_and_online import set_online, get_online


def load_job_if_not_current(job_name: str) -> None:
    if get_file() != job_name:
        if get_online() == 1:
            set_online(0)
        load_file(job_name)
        set_online(1)


def main():
    s = open_socket('192.168.103.2')
    log_cognex(s, 'admin', '')
    load_job_if_not_current('job1.job')
    if get_online() == 0:
        set_online(1)
    close_socket(s)
```

## Contributing 🤝

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.

## License 📝

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)