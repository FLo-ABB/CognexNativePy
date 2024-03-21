import re
import socket
from typing import Union

from CognexNativePy.CognexCommandError import CognexCommandError
from CognexNativePy.utils import receive_data, send_command, receive_data_from_socket, format_data


class SettingsAndCellsValues:
    def __init__(self, socket: socket.socket):
        self.socket = socket

    def get_value(self, cell_or_tag: str, row: int = None) -> str:
        """
        Returns the value contained in the specified cell or the contents of a specified symbolic tag.

        Args:
            cell_or_tag (str): The column letter of the cell value to get (A to Z) or the name of the symbolic tag.
            row (int, optional): The row number of the cell value to get. The row number must consist of three digits (000 to 399).
                                This parameter is ignored if cell_or_tag is a symbolic tag.

        Returns:
            str: The value contained in the specified cell or symbolic tag.

        Raises:
            ValueError: If the column is not a letter between A and Z or the row number is not between 0 and 399 (inclusive), or if the symbolic
                        tag is an empty string.
            CognexCommandError: If the command to retrieve the cell value or symbolic tag value fails.

        """
        if row is not None:
            if not re.match(r"^[A-Z]$", cell_or_tag):
                raise ValueError("The column must be a letter between A and Z.")
            if not 0 <= row <= 399:
                raise ValueError("The row number must be between 0 and 399 (inclusive).")
            formatted_row = f"{row:03d}"
            command = f"GV{cell_or_tag}{formatted_row}"
        else:
            if not cell_or_tag:
                raise ValueError("The symbolic tag cannot be an empty string.")
            command = f'GV{cell_or_tag}'

        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID or symbolic tag is invalid.",
            "-2": "The command could not be executed.",
        }

        if status_code == "1":
            value = data_received[1]
            return value
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_integer_value(self, cell_or_tag: str, row_or_value: int, value_if_cell: int = None) -> None:
        """
        Sets the value of the specified cell or symbolic tag to the specified integer value.

        Args:
            cell_or_tag (str): The column letter of the cell value to set (A to Z) or the name of the symbolic tag.
            row_or_value (int): If cell_or_tag is a column letter, this is the row number of the cell value to set.
                                If cell_or_tag is a symbolic tag, this is the integer value to set in the symbolic tag.
            value_if_cell (int, optional): If cell_or_tag is a column letter, this is the integer value to set in the cell.
                                            This parameter is ignored if cell_or_tag is a symbolic tag.

        Raises:
            ValueError: If the column is not a letter between A and Z or the row number is not between 0 and 399 (inclusive), or if the symbolic
                        tag is an empty string, or the value is not an integer.
            CognexCommandError: If the command to set the cell value or symbolic tag value fails.

        """
        if not isinstance(row_or_value, int):
            raise ValueError("The row number or value must be an integer.")

        if value_if_cell is not None:
            if not re.match(r"^[A-Z]$", cell_or_tag):
                raise ValueError("The column must be a letter between A and Z.")
            if not 0 <= row_or_value <= 399:
                raise ValueError("The row number must be between 0 and 399 (inclusive).")
            formatted_row = f"{row_or_value:03d}"
            command = f"SI{cell_or_tag}{formatted_row}{value_if_cell}"
        else:
            if not cell_or_tag:
                raise ValueError("The symbolic tag cannot be an empty string.")
            command = f'SI{cell_or_tag} {row_or_value}'

        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID or symbolic tag is invalid.",
            "-2": "The command could not be executed, or the specified integer value is outside of the control's valid range. For example,"
            "the specified cell may not contain a control of the valid type.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_float_value(self, cell_or_tag: str, row_or_value: int, value_if_cell: float = None) -> None:
        """
        Sets the value of the specified cell or symbolic tag to the specified float value.

        Args:
            cell_or_tag (str): The column letter of the cell value to set (A to Z) or the name of the symbolic tag.
            row_or_value (int): If cell_or_tag is a column letter, this is the row number of the cell value to set.
                                If cell_or_tag is a symbolic tag, this is the float value to set in the symbolic tag.
            value_if_cell (float, optional): If cell_or_tag is a column letter, this is the float value to set in the cell.
                                            This parameter is ignored if cell_or_tag is a symbolic tag.

        Raises:
            ValueError: If the column is not a letter between A and Z or the row number is not between 0 and 399 (inclusive), or if the symbolic tag
                        is an empty string, or the value is not a float.
            CognexCommandError: If the command to set the cell value or symbolic tag value fails.

        """
        if not isinstance(row_or_value, (int, float)):
            raise ValueError("The row number or value must be an integer or a float.")

        if value_if_cell is not None:
            if not re.match(r"^[A-Z]$", cell_or_tag):
                raise ValueError("The column must be a letter between A and Z.")
            if not 0 <= row_or_value <= 399:
                raise ValueError("The row number must be between 0 and 399 (inclusive).")
            if not isinstance(value_if_cell, float):
                raise ValueError("The value must be a float.")
            formatted_row = f"{row_or_value:03d}"
            command = f"SF{cell_or_tag}{formatted_row}{value_if_cell}"
        else:
            if not cell_or_tag:
                raise ValueError("The symbolic tag cannot be an empty string.")
            if not isinstance(row_or_value, float):
                raise ValueError("The value must be a float.")
            command = f'SF{cell_or_tag} {row_or_value}'

        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID or symbolic tag is invalid, or the specified value does not contain a floating-point number.",
            "-2": "The command could not be executed. For example, the specified cell may not contain an edit box control, or the"
            "edit box control was not created by the EditFloat function.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_region(
        self,
        cell_or_tag: str,
        row_or_row_offset: Union[int, float],
        row_offset_or_col_offset: Union[float, float],
        col_offset_or_high: Union[float, float],
        high_or_wide: Union[float, float],
        wide_or_angle: Union[float, float],
        angle_or_curve: Union[float, float],
        curve: float = None,
    ) -> None:
        """
        Sets an edit region control contained in a cell or a symbolic tag; the edit region control must be an EditRegion function.

        Args:
            cell_or_tag (str): The column letter of the cell value to set (A to Z) or the name of the symbolic tag.
            row_or_row_offset (int): If cell_or_tag is a column letter, this is the row number of the cell value to set.
                                If cell_or_tag is a symbolic tag, this is the x-offset of the origin, in image coordinates.
            row_offset_or_col_offset (float): If cell_or_tag is a column letter, this is the y-offset of the origin, in image coordinates.
                                              If cell_or_tag is a symbolic tag, this is the y-offset of the origin, in image coordinates.
            col_offset_or_high (float): If cell_or_tag is a column letter, this is the x-offset of the origin, in image coordinates.
                                        If cell_or_tag is a symbolic tag, this is the dimension along the region's x-axis.
            high_or_wide (float): If cell_or_tag is a column letter, this is the y-offset of the origin, in image coordinates.
                                  If cell_or_tag is a symbolic tag, this is the dimension along the region's y-axis.
            wide_or_angle (float): If cell_or_tag is a column letter, this is the dimension along the region's x-axis.
                                   If cell_or_tag is a symbolic tag, this is the orientation, in image coordinates.
            angle_or_curve (float): If cell_or_tag is a column letter, this is the orientation, in image coordinates.
                                    If cell_or_tag is a symbolic tag, this is the angle of orientation, in the image coordinate system.
            curve (float, optional): If cell_or_tag is a column letter, this is the angle of orientation, in the image coordinate system.
                                     This parameter is ignored if cell_or_tag is a symbolic tag.

        Returns:
            None

        Raises:
            ValueError: If the column is not a letter between A and Z or the row number is not between 0 and 399 (inclusive), or if any of the
                        offset, dimension, or angle values are not valid floating-point numbers.
            CognexCommandError: If the command to set the edit region control fails.

        """
        if not (
            isinstance(row_or_row_offset, (int, float))
            and isinstance(row_offset_or_col_offset, float)
            and isinstance(col_offset_or_high, float)
            and isinstance(high_or_wide, float)
            and isinstance(wide_or_angle, float)
            and isinstance(angle_or_curve, float)
        ):
            print(f'{isinstance(row_or_row_offset, (int, float))} {isinstance(row_offset_or_col_offset, float)} {
                isinstance(col_offset_or_high, float)} {isinstance(high_or_wide, float)} {isinstance(wide_or_angle, float)} {
                    isinstance(angle_or_curve, float)}')
            raise ValueError("Parameters has wrong types.")
        if curve is not None:
            if not re.match(r"^[A-Z]$", cell_or_tag):
                raise ValueError("The column must be a letter between A and Z.")
            if not 0 <= row_or_row_offset <= 399:
                raise ValueError("The row number must be between 0 and 399 (inclusive).")
            formatted_row = f"{row_or_row_offset:03d}"
            command = f"SR{cell_or_tag}{formatted_row}{row_offset_or_col_offset} {
                col_offset_or_high} {high_or_wide} {wide_or_angle} {angle_or_curve} {curve}"
        else:
            if not cell_or_tag:
                raise ValueError("The symbolic tag cannot be an empty string.")
            command = f'SR{cell_or_tag} {row_or_row_offset} {row_offset_or_col_offset} {
                col_offset_or_high} {high_or_wide} {wide_or_angle} {angle_or_curve}'

        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID or symbolic tag is invalid.",
            "-2": "The command could not be executed because the specified cell or symbolic tag does not contain an edit region control, or the edit"
                  "region control was not created by the EditRegion function.",
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_string(self, column: str, row: int, string_value: str) -> None:
        """
        Sets an edit box control contained in a cell to a specified string. The edit box must be of the type EditString.

        Args:
            column (str): The column letter of the cell value to set (A to Z).
            row (int): The row number of the cell value to set. The row number must contain a three-digit number (000 to 399).
            string_value (str): The string to set.

        Returns:
            None

        Raises:
            ValueError: If the column is not a letter between A and Z, the row number is not between 0 and 399 (inclusive), or the
                        string value is an empty string.
            CognexCommandError: If the command to set the string fails.

        """
        if not re.match(r"^[A-Z]$", column):
            raise ValueError("The column must be a letter between A and Z.")

        if not 0 <= row <= 399:
            raise ValueError("The row number must be between 0 and 399 (inclusive).")

        if not string_value:
            raise ValueError("The string value cannot be an empty string.")

        formatted_row = f"{row:03d}"
        command = f"SS{column}{formatted_row}{string_value}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid.",
            "-2": "The input string is longer than the specified maximum string length in the EditString function or the cell does not contain"
                  "an EditString function.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_info(self) -> dict:
        """
        Returns the system information for the In-Sight vision system.

        Returns:
            dict: A dictionary containing the system information.

        Raises:
            CognexCommandError: If the command to get the system information fails.

        """
        command = "GI"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The command could not be executed.",
        }

        if status_code == "1":
            system_info = {}
            info_lines = data_received[1:]
            for line in info_lines:
                if len(line.split(":")) == 2:
                    key, value = line.split(":")
                system_info[key.strip()] = value.strip()
            return system_info
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def read_settings(self) -> dict:
        """Reads the system settings data from an In-Sight sensor. The system settings data consist of the contents of the proc.set file,
           encoded in ASCII hexadecimal format.

        Returns:
            dict: A dictionary containing the system settings data.

        Raises:
            CognexCommandError: If the command to read the system settings data fails.

        """
        command = "RS"
        send_command(self.socket, command)
        data_received = receive_data_from_socket(self.socket, 'settings')
        status_code = data_received["status_code"]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The settings could not be read.",
            "-4": "The In-Sight sensor is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog.",
        }

        if status_code == "1":
            return {
                "size": data_received["size"],
                "settings": data_received["data"],
                "checksum": data_received["checksum"],
            }
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def write_settings(self, size: int, settings: str, checksum: str) -> None:
        """
        Sends the system settings data from a remote device to the In-Sight vision system.

        Note: The In-Sight sensor must be Offline.

        Args:
            size (int): The size (in bytes) of the settings.
            settings (str): The data for the settings, encoded as ASCII hexadecimal values formatted to 80 characters per line.
            checksum (str): Four ASCII hexadecimal bytes that are a checksum of the system settings data.

        Returns:
            None

        Raises:
            ValueError: If the size is not a positive integer, the settings string is empty, or the checksum string is empty.
            CognexCommandError: If the command to write the settings fails.

        """
        if size <= 0:
            raise ValueError("The size must be a positive integer.")

        if not settings or not checksum:
            raise ValueError("The settings and checksum strings must not be empty.")

        send_command(self.socket, "WS")
        send_command(self.socket, f"{size}")
        send_command(self.socket, f"{format_data(settings)}")
        send_command(self.socket, f"{checksum}")
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The settings could not be saved.",
            "-3": "The checksum failed. The checksum does not match the settings data.",
            "-4": "The In-Sight vision system is out of memory.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def store_settings(self) -> None:
        """
        Stores the In-Sight sensor settings to the proc.set file. For more information, see PROC.SET.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to store the settings fails.

        """
        command = "TS"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The sensor is Online, therefore the command could not be executed.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_ip_address_lock(self, lock: int) -> None:
        """
        Prevents unauthorized changes to an In-Sight sensor's IP address.

        Args:
            lock (int): 0 to unlock the IP address, 1 to lock the IP address.

        Returns:
            None

        Raises:
            ValueError: If the lock value is not 0 or 1.
            CognexCommandError: If the command to set the IP address lock fails.

        """
        if lock not in [0, 1]:
            raise ValueError("The lock value must be 0 or 1.")

        command = f"SL{lock}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The value given for Int is either out of range or is not a valid integer.",
            "-2": "The command could not be executed.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_ip_address_lock(self) -> int:
        """
        Returns the security status of the IP address on an In-Sight sensor.

        Returns:
            int: The security status of the IP address (0 for unlocked, 1 for locked).

        Raises:
            CognexCommandError: If the command to get the IP address lock fails.

        """
        command = "GL"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        return int(data_received[0])
