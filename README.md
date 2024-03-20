# 📷 🐍 pycognex 🐍 📷

`pycognex` is a Python wrapper for the Cognex native mode commands. It provides a simple and intuitive wrapper to interact with Cognex cameras. It's based on the Cognex native mode commands, which can be found in [Cognex Documentation Website](https://support.cognex.com/docs/is_590/web/EN/ise/Content/Communications_Reference/LoadFile.htm?tocpath=Communications%20Reference%7CNative%20Mode%20Communications%7CBasic%20Native%20Mode%20Commands%7CFile%20%26%20Job%20Commands%7C_____1).

## Table of Contents 📜

- [📷 🐍 pycognex 🐍 📷](#--pycognex--)
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

To use this library in your project, first download the repository and place the `pycognex` folder in your project's directory. You can then import the `NativeInterface` class from this library to interact with the Cognex camera. 

The `NativeInterface` class provides four categories of commands: `exectution_and_online`, `file_and_job`, `image`, and `settings_and_cell_value`. Each category corresponds to a set of related commands as documented in the [Cognex Documentation Website](https://support.cognex.com/docs/is_590/web/EN/ise/Content/Communications_Reference/LoadFile.htm?tocpath=Communications%20Reference%7CNative%20Mode%20Communications%7CBasic%20Native%20Mode%20Commands%7CFile%20%26%20Job%20Commands%7C_____1).

Each command category is an attribute of the `NativeInterface` class, allowing you to easily access and execute the commands you need for your specific use case.


## Usage 📚

Example of how to use the wrapper:
```python
from pycognex import NativeInterface


def main():
    try:
        # Create a socket connection to the Cognex In-Sight vision system and log in
        native_interface = NativeInterface('192.168.56.1', 'admin', '')
        execution_and_online = native_interface.execution_and_online
        file_and_job = native_interface.file_and_job
        image = native_interface.image

        # Load the job if it is not already loaded
        job_name = "myJob.job"
        if file_and_job.get_file() != job_name:
            if execution_and_online.get_online() == 1:
                execution_and_online.set_online(0)
                file_and_job.load_file(job_name)

        # Set the system online to be able to trigg the camera and get results
        if execution_and_online.get_online() == 0:
            execution_and_online.set_online(1)

        # Get the last image from the camera
        with open('image.bmp', 'wb') as f:
            f.write(image.read_image()["data"])

        # Close the socket connection
        native_interface.close()

    except Exception as e:
        print(f"Error: {e}")
```

## Contributing 🤝

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.

## License 📝

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

## Status 🚧

### File & Job Commands (13 commands)

| Command     | Implemented | Tested |
| ----------- | ----------- | ------ |
| Load File   | Yes         | Yes    |
| Store File  | Yes         | Yes    |
| Read File   | Yes         | Yes    |
| Write File  | Yes         | Yes    |
| Delete File | Yes         | Yes    |
| Get File    | Yes         | Yes    |
| Set Job     | Yes         | Yes    |
| Store Job   | Yes         | Yes    |
| Read Job    | Yes         | Yes    |
| Write Job   | Yes         | Yes    |
| Delete Job  | Yes         | Yes    |
| Get Job     | Yes         | Yes    |

### Image Commands (4 commands)

| Command     | Implemented | Tested |
| ----------- | ----------- | ------ |
| Read BMP    | Yes         | Yes    |
| Read Image  | Yes         | Yes    |
| Write BMP   | No          | No     |
| Write Image | No          | No     |

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
| Set Online         | Yes         | Yes    |
| Get Online         | Yes         | Yes    |
| Set Event          | Yes         | Yes    |
| Set Event and Wait | Yes         | Yes    |
| Reset System       | Yes         | No     |
| Send Message       | Yes         | Yes    |

## Key Performance Indicators 🎯

| Indicator                     | Count |
| ----------------------------- | ----- |
| Total of commands             | 34    |
| Total of implemented commands | 21    |
| Total of tested commands      | 18    |

### Progress 

🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛ : Implementation

🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛  : Testing
