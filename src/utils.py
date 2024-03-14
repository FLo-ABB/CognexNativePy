import socket
from CognexCommandError import CognexCommandError
import textwrap

PORT = 23


def send_command(socket: socket.socket, string_command: str):
    """
    Sends a command to the specified socket.

    Args:
        socket (socket.socket): The socket to send the command to.
        string_command (str): The command to send.

    Returns:
        None
    """
    command = string_command.encode('ascii') + b'\r\n'
    socket.sendall(command)


def receive_data(socket: socket.socket) -> str:
    """
    Receives data from the given socket and returns it as a string.

    Args:
        socket (socket.socket): The socket to receive data from.

    Returns:
        str: The received data as a string.
    """
    data = socket.recv(1024)
    string_data = data.decode('ascii').replace('\r\n', '')
    return string_data


def open_socket(host_adress: str) -> socket.socket:
    """
    Opens a socket connection to the specified host address.

    Args:
        host_adress (str): The IP address or hostname of the remote host.

    Returns:
        socket.socket: The socket object representing the connection.

    Raises:
        OSError: If an error occurs while opening the socket.

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_adress, PORT))
    data_received = receive_data(s)
    if not (data_received.startswith('Welcome')):
        raise CognexCommandError(f'Error logging in, expected "Welcome [...]", received "{data_received}"')
    else:
        return s


def close_socket(socket: socket.socket) -> None:
    """
    Closes the given socket.

    Args:
        socket (socket.socket): The socket to be closed.

    Returns:
        None
    """
    socket.close()


def login_to_cognex_system(socket: socket.socket, user: str, password: str):
    """
    Logs into the Cognex system using the provided socket, user, and password.

    Args:
        socket (socket.socket): The socket connection to the Cognex system.
        user (str): The username to log in with.
        password (str): The password to log in with.

    Returns:
        None
    """
    expected_responses = ['User: ', 'Password: ', 'User Logged In']
    commands = [user, password, None]
    for expected_response, command in zip(expected_responses, commands):
        if receive_data(socket) == expected_response:
            if command is not None:
                send_command(socket, command)
        else:
            raise CognexCommandError(f'Error logging in, expected "{expected_response}"')


def hex_to_bytes(hex_string: str) -> bytes:
    """
    Converts a hexadecimal string to bytes.

    Args:
        hex_string (str): The hexadecimal string to convert.

    Returns:
        bytes: The converted bytes.

    Raises:
        ValueError: If the input string is not a valid hexadecimal string.

    Example:
        >>> hex_to_bytes('48656c6c6f20576f726c64')
        b'Hello World'
    """
    return bytes.fromhex(hex_string)


def format_job_data(data: bytes):
    """
    Formats the given data as a hexadecimal string with a maximum of 80 characters per line.

    Args:
        data (bytes): The data to be formatted.

    Returns:
        str: The formatted hexadecimal string.
    """
    hex_data = data.hex()
    formatted_hex_data = textwrap.wrap(hex_data, 80)
    return "\n".join(formatted_hex_data)
