import select
import socket
import textwrap
import time
import weakref

from CognexNativePy.CognexCommandError import CognexCommandError

PORT = 23
DEBUG = False
_LINE_END = b'\r\n'
_RECEIVE_TIMEOUT_SECONDS = 30.0
_RECV_CHUNK_BYTES = 4096
_MAX_BUFFERED_BYTES = 64 * 1024
_READERS = weakref.WeakKeyDictionary()


class _SocketReader:
    """Buffers a socket byte stream until complete protocol frames exist."""

    def __init__(self, connection: socket.socket):
        self._connection = weakref.ref(connection)
        self.buffer = bytearray()
        self.invalid = False

    @property
    def connection(self) -> socket.socket:
        connection = self._connection()
        if connection is None:
            raise CognexCommandError("Socket session is no longer usable.")
        return connection

    def _fail(self, message: str):
        self.invalid = True
        self.buffer.clear()
        try:
            self.connection.close()
        finally:
            raise CognexCommandError(message)

    def _receive_more(self, deadline: float) -> None:
        if self.invalid:
            raise CognexCommandError("Socket session is no longer usable.")

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            self._fail("Timed out while receiving a complete response.")

        previous_timeout = None
        timeout_supported = hasattr(self.connection, 'gettimeout') and hasattr(self.connection, 'settimeout')
        if timeout_supported:
            previous_timeout = self.connection.gettimeout()
            self.connection.settimeout(remaining)

        try:
            chunk = self.connection.recv(_RECV_CHUNK_BYTES)
        except (socket.timeout, TimeoutError):
            self._fail("Timed out while receiving a complete response.")
        except OSError:
            self._fail("Socket error while receiving a response.")
        finally:
            if timeout_supported and not self.invalid:
                self.connection.settimeout(previous_timeout)

        if not chunk:
            self._fail("Connection closed before a complete response was received.")
        if len(self.buffer) + len(chunk) > _MAX_BUFFERED_BYTES:
            self._fail("Response exceeded the maximum buffered size.")
        self.buffer.extend(chunk)

    def read_line(self, deadline: float) -> str:
        while True:
            end = self.buffer.find(_LINE_END)
            if end >= 0:
                line = bytes(self.buffer[:end])
                del self.buffer[:end + len(_LINE_END)]
                try:
                    return line.decode('ascii')
                except UnicodeDecodeError:
                    self._fail("Response contained non-ASCII data.")
            self._receive_more(deadline)

    def read_bytes(self, size: int, deadline: float) -> bytes:
        while len(self.buffer) < size:
            self._receive_more(deadline)
        data = bytes(self.buffer[:size])
        del self.buffer[:size]
        return data

    def read_prompt(self, prompt: bytes, deadline: float) -> None:
        while True:
            if self.buffer == prompt:
                self.buffer.clear()
                return
            if self.buffer and not prompt.startswith(self.buffer):
                self._fail("Unexpected login prompt received.")
            self._receive_more(deadline)

    def finish_response(self) -> None:
        if self.buffer:
            self._fail("Unexpected data remained after the response.")

    def ensure_can_send(self) -> None:
        if self.invalid:
            raise CognexCommandError("Socket session is no longer usable.")
        if self.buffer:
            self._fail("Unexpected data was pending before a command.")
        try:
            readable, _, _ = select.select([self.connection], [], [], 0)
        except (OSError, TypeError, ValueError):
            return
        if not readable:
            return
        try:
            pending = self.connection.recv(1, socket.MSG_PEEK)
        except (BlockingIOError, socket.timeout):
            return
        except OSError:
            self._fail("Socket error while checking pending data.")
        if pending:
            self._fail("Unexpected data was pending before a command.")
        self._fail("Connection was closed before a command was sent.")


def _get_reader(connection: socket.socket) -> _SocketReader:
    reader = _READERS.get(connection)
    if reader is None:
        reader = _SocketReader(connection)
        _READERS[connection] = reader
    return reader


def _deadline() -> float:
    return time.monotonic() + _RECEIVE_TIMEOUT_SECONDS


def _receive_exact_lines(connection: socket.socket, line_count: int) -> list:
    reader = _get_reader(connection)
    deadline = _deadline()
    lines = [reader.read_line(deadline) for _ in range(line_count)]
    reader.finish_response()
    return lines


def _receive_status_response(connection: socket.socket, successful_value_lines: int = 0) -> list:
    reader = _get_reader(connection)
    deadline = _deadline()
    status = reader.read_line(deadline)
    response = [status]
    if status == "1":
        response.extend(reader.read_line(deadline) for _ in range(successful_value_lines))
    else:
        response.extend('' for _ in range(successful_value_lines))
    reader.finish_response()
    return response


def _receive_sized_response(connection: socket.socket) -> list:
    reader = _get_reader(connection)
    deadline = _deadline()
    status = reader.read_line(deadline)
    if status != "1":
        reader.finish_response()
        return [status, '']

    try:
        payload_size = int(reader.read_line(deadline))
    except ValueError:
        reader._fail("Response contained an invalid payload size.")
    if payload_size < 0:
        reader._fail("Response contained an invalid payload size.")
    payload = reader.read_bytes(payload_size, deadline)
    if reader.read_bytes(len(_LINE_END), deadline) != _LINE_END:
        reader._fail("Response payload was not terminated by CRLF.")
    try:
        decoded_payload = payload.decode('ascii')
    except UnicodeDecodeError:
        reader._fail("Response contained non-ASCII data.")
    reader.finish_response()
    return [status, decoded_payload]


def send_command(socket: socket.socket, string_command: str):
    """
    Sends a command to the specified socket.

    Args:
        socket (socket.socket): The socket to send the command to.
        string_command (str): The command to send.

    Returns:
        None
    """
    _get_reader(socket).ensure_can_send()
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
    reader = _get_reader(socket)
    deadline = _deadline()
    string_data = [reader.read_line(deadline)]
    while reader.buffer.find(_LINE_END) >= 0:
        string_data.append(reader.read_line(deadline))
    string_data.append('')
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
    s.settimeout(_RECEIVE_TIMEOUT_SECONDS)
    try:
        s.connect((host_adress, PORT))
        data_received = _get_reader(s).read_line(_deadline())
        if not (data_received.startswith('Welcome')):
            close_socket(s)
            raise CognexCommandError(f'Error logging in, expected "Welcome [...]", received "{data_received}"')
        else:
            return s
    except socket.timeout:
        close_socket(s)
        raise CognexCommandError(f'Connection attempt to {host_adress} timed out')


def close_socket(socket: socket.socket) -> None:
    """
    Closes the given socket.

    Args:
        socket (socket.socket): The socket to be closed.

    Returns:
        None
    """
    _READERS.pop(socket, None)
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
    reader = _get_reader(socket)
    deadline = _deadline()
    reader.read_prompt(b'User: ', deadline)
    send_command(socket, user)
    reader.read_prompt(b'Password: ', deadline)
    send_command(socket, password)
    if reader.read_line(deadline) != 'User Logged In':
        reader._fail('Error logging in, expected "User Logged In"')
    reader.finish_response()


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


def calculate_checksum(buffer: bytes) -> int:
    """
    Calculate the CRC for the given buffer.

    Args:
        buffer (bytes): The input buffer.

    Returns:
        int: The calculated CRC value (unsigned short).
    """
    if all(48 <= byte <= 57 or 65 <= byte <= 70 or 97 <= byte <= 102 for byte in buffer):
        ascii_hex_buffer = buffer
    else:
        ascii_hex_buffer = hex_to_ascii_hex(buffer)
    cword = 0  # Initialize CRC word
    for byte in ascii_hex_buffer:
        ch = byte << 8  # Shift byte to the left by 8 bits
        for _ in range(8):  # Process each bit
            if ((ch & 0x8000) ^ (cword & 0x8000)):  # Check if MSB differs
                cword = (cword << 1) ^ 4129  # XOR with the polynomial
            else:
                cword <<= 1  # Shift left without XOR
            cword &= 0xFFFF  # Ensure cword stays within 16 bits
            ch <<= 1  # Shift ch to the left
    return "{:04X}".format(cword)


def hex_to_ascii_hex(buffer: bytes) -> bytes:
    """
    Convert a buffer to its ASCII hex representation.

    Args:
        buffer (bytes): The input buffer.

    Returns:
        bytes: The ASCII hex representation of the buffer.
    """
    return ''.join(f'{byte:02X}' for byte in buffer).encode('ascii')
