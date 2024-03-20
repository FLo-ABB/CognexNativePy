import socket
import re

from pycognex.CognexCommandError import CognexCommandError
from pycognex.utils import send_command, receive_data


class SettingsAndCellsValues:
    def __init__(self, socket: socket.socket):
        self.socket = socket

    def get_value_spreadsheet_view(self, column: str, row: int) -> str:
        """
        Returns the value contained in the specified spreadsheet cell.

        Args:
            column (str): The column letter of the cell value to get (A to Z).
            row (int): The row number of the cell value to get. The row number must consist of three digits (000 to 399).

        Returns:
            str: The value contained in the specified cell.

        Raises:
            ValueError: If the column is not a letter between A and Z or the row number is not between 0 and 399 (inclusive).
            CognexCommandError: If the command to retrieve the cell value fails.

        """
        if not re.match(r"^[A-Z]$", column):
            raise ValueError("The column must be a letter between A and Z.")

        if not 0 <= row <= 399:
            raise ValueError("The row number must be between 0 and 399 (inclusive).")

        formatted_row = f"{row:03d}"
        command = f"GV{column}{formatted_row}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid.",
            "-2": "The command could not be executed.",
        }

        if status_code == "1":
            cell_value = data_received[1]
            return cell_value
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_value_easybuilder_view(self, symbolic_tag: str) -> str:
        """
        Returns the contents of a specified symbolic tag, such as an EasyBuilder Location or Inspection Tool result or job data.

        Args:
            symbolic_tag (str): The name of the symbolic tag, such as a Location or Inspection Tool result or job data (for example,
            "Job.Robot.FormatString.", "Job.FormatString").

        Returns:
            str: The value contained in the specified symbolic tag.

        Raises:
            ValueError: If the symbolic tag is an empty string.
            CognexCommandError: If the command to retrieve the symbolic tag value fails.

        """
        if not symbolic_tag:
            raise ValueError("The symbolic tag cannot be an empty string.")
        command = f'GV{symbolic_tag}'
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": 'The "Symbolic Tag" is invalid.',
            "-2": "The command could not be executed.",
        }

        if status_code == "1":

            tag_value = data_received[1]
            return tag_value
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_integer_spreadsheet_view(self, column: str, row: int, value: int) -> None:
        """
        Sets the value of the specified spreadsheet cell to the specified integer value.

        Args:
            column (str): The column letter of the cell value to set (A to Z).
            row (int): The row number of the cell value to set. The row number must consist of three digits (000 to 399).
            value (int): The integer value to set in the specified cell.

        Raises:
            ValueError: If the column is not a letter between A and Z, the row number is not between 0 and 399 (inclusive), or the value is not
                        an integer.
            CognexCommandError: If the command to set the cell value fails.

        """
        if not re.match(r"^[A-Z]$", column):
            raise ValueError("The column must be a letter between A and Z.")

        if not 0 <= row <= 399:
            raise ValueError("The row number must be between 0 and 399 (inclusive).")

        if not isinstance(value, int):
            raise ValueError("The value must be an integer.")

        formatted_row = f"{row:03d}"
        command = f"SI{column}{formatted_row}{value}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid.",
            "-2": "The command could not be executed, or the specified integer value is outside of the control's valid range. For example,"
                  "the specified cell may not contain a control of the valid type.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_integer_easybuilder_view(self, symbolic_tag: str, value: int) -> None:
        """
        Sets the value of the specified symbolic tag to the specified integer value.

        Args:
            symbolic_tag (str): The name of the symbolic tag, such as a Location or Inspection Tool result or job data (for example,
                                "Job.Robot.FormatString.", "Job.FormatString").
            value (int): The integer value to set in the specified symbolic tag.

        Raises:
            ValueError: If the symbolic tag is an empty string or the value is not an integer.
            CognexCommandError: If the command to set the symbolic tag value fails.

        """
        if not symbolic_tag:
            raise ValueError("The symbolic tag cannot be an empty string.")

        if not isinstance(value, int):
            raise ValueError("The value must be an integer.")

        command = f'SI{symbolic_tag} {value}'
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid.",
            "-2": "The command could not be executed, or the specified integer value is outside of the control's valid range. For example,"
                  "the specified cell may not contain a control of the valid type.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_float_spreadsheet_view(self, column: str, row: int, value: float) -> None:
        """
        Sets the value of the specified spreadsheet cell to the specified float value.

        Args:
            column (str): The column letter of the cell value to set (A to Z).
            row (int): The row number of the cell value to set. The row number must consist of three digits (000 to 399).
            value (float): The floating-point value to set, including the decimal point (.) character.
        Raises:
            ValueError: If the column is not a letter between A and Z, the row number is not between 0 and 399 (inclusive), or the value is not
                        a float.
            CognexCommandError: If the command to set the cell value fails.
        """
        if not re.match(r"^[A-Z]$", column):
            raise ValueError("The column must be a letter between A and Z.")

        if not 0 <= row <= 399:
            raise ValueError("The row number must be between 0 and 399 (inclusive).")

        if not isinstance(value, float):
            raise ValueError("The value must be a float.")

        formatted_row = f"{row:03d}"
        command = f"SF{column}{formatted_row}{value}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid, or the specified value does not contain a floating-point number.",
            "-2": "The command could not be executed. For example, the specified cell may not contain an edit box control, or the"
                  "edit box control was not created by the EditFloat function.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_float_easybuilder_view(self, symbolic_tag: str, value: float) -> None:
        """
        Sets the value of the specified symbolic tag to the specified float value.

        Args:
            symbolic_tag (str): The name of the symbolic tag, such as a Location or Inspection Tool result or job data (for example,
                                "Job.Robot.FormatString.", "Job.FormatString").
            value (float): The floating-point value to set, including the decimal point (.) character.

        Raises:
            ValueError: If the symbolic tag is an empty string or the value is not a float.
            CognexCommandError: If the command to set the symbolic tag value fails.

        """
        if not symbolic_tag:
            raise ValueError("The symbolic tag cannot be an empty string.")

        if not isinstance(value, float):
            raise ValueError("The value must be a float.")

        command = f'SF{symbolic_tag} {value}'
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The cell ID is invalid, or the specified value does not contain a floating-point number.",
            "-2": "The command could not be executed. For example, the specified cell may not contain an edit box control, or the"
                  "edit box control was not created by the EditFloat function.",
            "-6": "User does not have Full Access to execute the command. For more information, see User Access Settings Dialog."
        }

        if status_code != "1":
            if status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
