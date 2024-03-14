# 📷 🐍 NativeCognexPythonWrapper 🐍 📷

WORK IN PROGRESS, see the [Status](#status-) section for more information.

NativeCognexPythonWrapper is a Python wrapper for the Cognex native mode commands. It provides a simple and intuitive wrapper to interact with Cognex cameras. It's based on the Cognex native mode commands, which can be found in [Cognex Documentation Website](https://support.cognex.com/docs/is_590/web/EN/ise/Content/Communications_Reference/LoadFile.htm?tocpath=Communications%20Reference%7CNative%20Mode%20Communications%7CBasic%20Native%20Mode%20Commands%7CFile%20%26%20Job%20Commands%7C_____1).

## Table of Contents 📜

- [📷 🐍 NativeCognexPythonWrapper 🐍 📷](#--nativecognexpythonwrapper--)
  - [Table of Contents 📜](#table-of-contents-)
  - [Installation 🚀](#installation-)
  - [Usage 📚](#usage-)
  - [Contributing 🤝](#contributing-)
  - [License 📝](#license-)
  - [Status 🚧](#status-)
    - [File \& Job Commands (13 commands)](#file--job-commands-13-commands)
    - [Image Commands (4 commands)](#image-commands-4-commands)
    - [Settings \& Cell Value Commands (11 commands)](#settings--cell-value-commands-11-commands)
    - [Execution \& Online Commands (6 commands)](#execution--online-commands-6-commands)
  - [Key Performance Indicators 🎯](#key-performance-indicators-)
    - [Progress](#progress)

## Installation 🚀

Download the repository and import the src folder into your project. The wrapper is divided into two main modules: `utils` and `commands`. The `utils` module contains the low-level functions to open and close a socket, and to log into the Cognex camera. The `commands` module contains the high-level functions to interact with the camera, such as loading a file, setting the camera online, and getting the current online status. Look over the `sandbox.py` file to see how to use the wrapper.

## Usage 📚

Example of how to use the wrapper:
```python
from utils import open_socket, close_socket, login_to_cognex_system
from commands.file_and_job import load_file, get_file
from commands.execution_and_online import set_online, get_online


def load_job_if_not_current(job_name: str) -> None:
    if get_file() != job_name:
        if get_online() == 1:
            set_online(0)
        load_file(job_name)
        set_online(1)


def set_system_online() -> None:
    if get_online() == 0:
        set_online(1)


def main():
    s = open_socket('192.168.103.2')
    login_to_cognex_system(s, 'admin', '')
    load_job_if_not_current('job1.job')
    set_system_online()
    close_socket(s)
```

## Contributing 🤝

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.

## License 📝

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Status 🚧

### File & Job Commands (13 commands)

| Command     | Implemented | Tested |
| ----------- | ----------- | ------ |
| Load File   | Yes         | No     |
| Store File  | Yes         | No     |
| Read File   | Yes         | No     |
| Write File  | Yes         | No     |
| Delete File | Yes         | No     |
| Get File    | Yes         | No     |
| Set Job     | Yes         | No     |
| Store Job   | Yes         | No     |
| Read Job    | Yes         | No     |
| Write Job   | Yes         | No     |
| Delete Job  | Yes         | No     |
| Get Job     | Yes         | No     |

### Image Commands (4 commands)

| Command     | Implemented | Tested |
| ----------- | ----------- | ------ |
| Read BMP    | Yes         | No     |
| Read Image  | Yes         | No     |
| Write BMP   | Yes         | No     |
| Write Image | Yes         | No     |

### Settings & Cell Value Commands (11 commands)

| Command             | Implemented | Tested |
| ------------------- | ----------- | ------ |
| Get Value           | No          | No     |
| Set Integer         | No          | No     |
| Set Float           | No          | No     |
| Set Region          | No          | No     |
| Set String          | No          | No     |
| Get Info            | No          | No     |
| Read Settings       | No          | No     |
| Write Settings      | No          | No     |
| Store Settings      | No          | No     |
| Set IP Address Lock | No          | No     |
| Get IP Address Lock | No          | No     |

### Execution & Online Commands (6 commands)

| Command            | Implemented | Tested |
| ------------------ | ----------- | ------ |
| Set Online         | Yes         | No     |
| Get Online         | Yes         | No     |
| Set Event          | No          | No     |
| Set Event and Wait | No          | No     |
| Reset System       | No          | No     |
| Send Message       | No          | No     |

## Key Performance Indicators 🎯

| Indicator                     | Count |
| ----------------------------- | ----- |
| Total of commands             | 34    |
| Total of implemented commands | 24    |
| Total of tested commands      | 0     |

### Progress 

🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛ : Implementation

⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  : Testing
