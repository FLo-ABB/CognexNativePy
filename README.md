# 📷 🐍 CognexNativePy 🐍 📷

`CognexNativePy` is a Python wrapper for the Cognex native mode commands. It provides a simple and intuitive wrapper to interact with Cognex cameras. It's based on the Cognex native mode commands, which can be found in [Cognex Documentation Website](https://support.cognex.com/docs/is_590/web/EN/ise/Content/Communications_Reference/LoadFile.htm?tocpath=Communications%20Reference%7CNative%20Mode%20Communications%7CBasic%20Native%20Mode%20Commands%7CFile%20%26%20Job%20Commands%7C_____1).

## Table of Contents 📜

- [📷 🐍 CognexNativePy 🐍 📷](#--cognexnativepy--)
  - [Table of Contents 📜](#table-of-contents-)
  - [Installation 🚀](#installation-)
  - [Usage 📚](#usage-)
  - [Contributing 🤝](#contributing-)
  - [License 📝](#license-)

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
        settings_and_cells_values = native_interface.settings_and_cells_values

        # Load the job if it is not already loaded
        job_name = "1myJob.job"
        if file_and_job.get_file() != job_name:
            if execution_and_online.get_online() == 1:
                execution_and_online.set_online(0)
            file_and_job.load_file(job_name)

        # Get the last image from the camera and save it as a BMP file
        with open('image.bmp', 'wb') as f:
            f.write(image.read_image()["data"])

        # Get the value of the cell B010 (spreadsheet view)
        print(settings_and_cells_values.get_value("B", 10))
        # Set the value of the cell D019 (spreadsheet view) to 53
        settings_and_cells_values.set_integer_value("D", 19, 53)
        # Set the value of the symbolic tag "Pattern_1.Horizontal_Offset" to 69.3 (EasyBuilder view)
        settings_and_cells_values.set_float_value("Pattern_1.Horizontal_Offset", 69.3)
        # Get the information of the settings and cells values
        print(settings_and_cells_values.get_info())

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