import socket

from pycognex.CognexCommandError import CognexCommandError
from pycognex.utils import receive_image_data, send_command


class Image:
    def __init__(self, socket: socket.socket):
        self.socket = socket

    def read_bmp(self) -> dict:
        """
        Sends the current image from an In-Sight sensor to a remote device. The image is sent in ASCII hexadecimal format.

        Returns:
            dict: A dictionary containing the following keys:
                - 'size': The size of the image file in bytes.
                - 'data': The image data in ASCII hexadecimal format. This data can be converted to a BMP file using the following code:
                    with open('image.bmp', 'wb') as f:
                        f.write(read_bmp()["data"])
                - 'checksum': A checksum of the image data, represented as four ASCII hexadecimal bytes.

        Raises:
            CognexCommandError: If there is an error executing the command to retrieve the image data.
        """
        command = "RB"
        send_command(self.socket, command)
        data_received = receive_image_data(self.socket)
        status_code = data_received["status_code"]
        image_size = data_received["size"]
        image_data_bytes = data_received["data"]
        image_checksum = data_received["checksum"]

        status_messages = {
            "0": "Unrecognized command.",
            "-4": "The In-Sight sensor is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return {
                "size": image_size,
                "data": image_data_bytes,
                "checksum": image_checksum,
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
        send_command(self.socket, command)
        data_received = receive_image_data(self.socket)
        status_code = data_received["status_code"]
        image_size = data_received["size"]
        image_data_bytes = data_received["data"]
        image_checksum = data_received["checksum"]

        status_messages = {
            0: "Unrecognized command.",
            -4: "The In-Sight sensor is out of memory.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return {
                "size": image_size,
                "data": image_data_bytes,
                "checksum": image_checksum,
            }
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

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
        # TODO
        # status_messages = {
        #     "0": "Unrecognized command.",
        #     "-2": "The image could not be written, or the image data is invalid.",
        #     "-3": "The checksum failed. The checksum does not match the image data.",
        #     "-4": "The In-Sight sensor is out of memory.",
        #     "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        # }

        # if status_code == "1":
        #     return None
        # elif status_code in status_messages:
        #     raise CognexCommandError(status_messages[status_code])
        # else:
        #     raise CognexCommandError(f"Unknown status code: {status_code}")

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
        # TODO

        # status_messages = {
        #     "0": "Unrecognized command.",
        #     "-2": "The image could not be written, or the image data is invalid.",
        #     "-3": "The checksum failed. The checksum does not match the image data.",
        #     "-4": "The In-Sight sensor is out of memory.",
        #     "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        # }

        # if status_code == "1":
        #     return None
        # elif status_code in status_messages:
        #     raise CognexCommandError(status_messages[status_code])
        # else:
        #     raise CognexCommandError(f"Unknown status code: {status_code}")
