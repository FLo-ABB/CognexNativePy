import socket
import textwrap

from CognexNativePy.CognexCommandError import CognexCommandError

PORT = 23
DEBUG = False


def send_command(socket: socket.socket, string_command: str):
    """
    Sends a command to the specified socket.

    Args:
        socket (socket.socket): The socket to send the command to.
        string_command (str): The command to send.

    Returns:
        None
    """
    if DEBUG:
        with open('out.txt', 'a') as f:
            f.write(string_command+'\n')
    command = string_command.encode('ascii') + b'\r\n'
    socket.sendall(command)


def receive_data(socket: socket.socket) -> list:
    """
    Receives data from the given socket and returns it as a list of strings.

    Args:
        socket (socket.socket): The socket to receive data from.

    Returns:
        list: The received data as a list of strings.
    """
    data = socket.recv(4096)
    string_data = data.decode('ascii').split('\r\n')
    if DEBUG:
        with open('in.txt', 'a') as f:
            f.write("\n".join(string_data))
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
    try:
        s.connect((host_adress, PORT))
        data_received = receive_data(s)[0]
        if not (data_received.startswith('Welcome')):
            raise CognexCommandError(f'Error logging in, expected "Welcome [...]", received "{data_received}"')
        else:
            return s
    except socket.timeout:
        raise CognexCommandError(f'Connection attempt to {host_adress} timed out')


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
        user (str): The username to log in with (default is 'admin').
        password (str): The password to log in with (default is '')

    Returns:
        None
    """
    expected_responses = ['User: ', 'Password: ', 'User Logged In']
    commands = [user, password, None]
    for expected_response, command in zip(expected_responses, commands):
        if receive_data(socket)[0] == expected_response:
            if command is not None:
                send_command(socket, command)
        else:
            raise CognexCommandError(f'Error logging in, expected "{expected_response}"')


def format_data(data: bytes):
    """
    Formats the given data as a hexadecimal string with a maximum of 80 characters per line.

    Args:
        data (bytes): The data to be formatted.

    Returns:
        str: The formatted hexadecimal string.
    """
    hex_data = data.hex().upper()
    formatted_hex_data = textwrap.wrap(hex_data, 80)
    return "\r\n".join(formatted_hex_data)


def receive_data_from_socket(socket: socket.socket, data_type: str) -> dict:
    """
    Receives data from the given socket.

    Args:
        socket (socket.socket): The socket to receive data from.
        data_type (str): The type of data to receive. Should be either 'image', 'file', 'job' or 'settings'.

    Returns:
        dict: A dictionary containing the received data.
    """
    if data_type not in ['image', 'file', 'job', 'settings']:
        raise ValueError(f"Invalid data type: {data_type}, accepted values are 'image', 'file' and 'job'")
    data_received = receive_data(socket)
    status_code = data_received[0]
    size = int(data_received[1 if (data_type == 'image' or data_type == 'settings') else 2])
    data = b''
    # size is divided by 2 because the data is in hexadecimal format
    while len(data) < size/2:
        data_received = receive_data(socket)
        for received in data_received:
            data += bytes.fromhex(received)
    if data_type == 'image':
        check_sum = data_received[-2]
        data = data[:-2]
    else:
        check_sum = receive_data(socket)[0]
    return_dict = {
        "status_code": status_code,
        "size": size,
        "data": data,
        "checksum": check_sum
    }
    if status_code == "1":
        if (data_type == 'file' or data_type == 'job'):
            return_dict["file_name"] = data_received[1]
        return return_dict
    else:
        return {"status_code": status_code}
