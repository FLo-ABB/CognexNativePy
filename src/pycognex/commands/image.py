from pycognex.CognexCommandError import CognexCommandError
from pycognex.utils import send_command, hex_to_bytes, receive_data
import textwrap
import socket


class Image:
    def __init__(self, socket: socket.socket):
        self.socket = socket

    def read_bmp(self) -> dict:
        """
        Sends the current image, in ASCII hexadecimal format, from an In-Sight sensor out to a remote device.

        Returns:
            dict: A dictionary containing the image data.

        Raises:
            CognexCommandError: If the command to retrieve the image data fails.

        """
        command = "RB"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        print(f"data_received: {data_received}")
        status_code = data_received[0]
        size = data_received[1]
        print(f"size: {size}")
        print(f"status_code: {status_code}")

        status_messages = {
            "0": "Unrecognized command.",
            "-4": "The In-Sight sensor is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            image_size = size  # in bytes

            return {
                "size": image_size,
                "data": "image_data_bytes",
                "checksum": "image_checksum",
            }
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def read_image(self) -> dict:
        """
        Sends the current image, in ASCII hexadecimal format, from an In-Sight sensor out to a remote device.

        Returns:
            dict: A dictionary containing the image data.

        Raises:
            CognexCommandError: If the command to retrieve the image data fails.

        """
        command = "RI"
        status_code, image_data = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -4: "The In-Sight sensor is out of memory.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        try:
            if status_code == 1:
                image_data_lines = image_data.strip().split("\n")
                if len(image_data_lines) < 3:
                    raise CognexCommandError("Invalid image data format.")

                image_size = int(image_data_lines[0])
                image_data_hex = "".join(image_data_lines[1:-1]).replace(" ", "")
                image_data_bytes = hex_to_bytes(image_data_hex)
                image_checksum = image_data_lines[-1]

                return {
                    "size": image_size,
                    "data": image_data_bytes,
                    "checksum": image_checksum,
                }
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error reading image: {e}")
            return None

    def write_bmp(self, image_size: int, image_data: bytes, image_checksum: str) -> None:
        """
        Sends image data from a remote device to an In-Sight sensor.

        Args:
            image_size (int): An integer value for the size (in bytes) of the image file.
            image_data (bytes): The actual image data.
            image_checksum (str): Four ASCII hexadecimal bytes that are a checksum of the image data.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to write the image data fails.

        """
        image_data_hex = " ".join(textwrap.wrap(image_data.hex(), 80))
        command = f"WB[{image_size}][{image_data_hex}][{image_checksum}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -2: "The image could not be written, or the image data is invalid.",
            -3: "The checksum failed. The checksum does not match the image data.",
            -4: "The In-Sight sensor is out of memory.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        try:
            if status_code == 1:
                return None
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error writing image: {e}")
            return None

    def write_image(self, image_size: int, image_data: bytes, image_checksum: str) -> None:
        """
        Sends image data from a remote device to an In-Sight sensor.

        Args:
            image_size (int): An integer value for the size, in bytes, of the image file.
            image_data (bytes): The actual image data.
            image_checksum (str): Four ASCII hexadecimal bytes that are a checksum of the image data.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to write the image data fails.

        """
        image_data_hex = " ".join(textwrap.wrap(image_data.hex(), 80))
        command = f"WI[{image_size}][{image_data_hex}][{image_checksum}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -2: "The image could not be written, or the image data is invalid.",
            -3: "The checksum failed. The checksum does not match the image data.",
            -4: "The In-Sight sensor is out of memory.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        try:
            if status_code == 1:
                return None
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error writing image: {e}")
            return None
