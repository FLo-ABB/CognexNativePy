import inspect
import socket
import sys
import unittest
from collections import deque
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from CognexNativePy.CognexCommandError import CognexCommandError
from CognexNativePy.commands.ExecutionAndOnline import ExecutionAndOnline
from CognexNativePy.commands.FileAndJob import FileAndJob
from CognexNativePy.commands.SettingsAndCellsValues import SettingsAndCellsValues
from CognexNativePy.utils import (
    _MAX_BUFFERED_BYTES,
    _receive_status_response,
    login_to_cognex_system,
    open_socket,
    receive_data,
    send_command,
)


class FakeSocket:
    def __init__(self, chunks=(), connect_error=None):
        self.chunks = deque(chunks)
        self.connect_error = connect_error
        self.connected_to = None
        self.sent = []
        self.timeout = None
        self.timeout_history = []
        self.closed = False

    def connect(self, address):
        self.connected_to = address
        if self.connect_error is not None:
            raise self.connect_error

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, size, flags=0):
        if not self.chunks:
            raise socket.timeout()
        chunk = self.chunks.popleft()
        if isinstance(chunk, BaseException):
            raise chunk
        return chunk

    def gettimeout(self):
        return self.timeout

    def settimeout(self, timeout):
        self.timeout = timeout
        self.timeout_history.append(timeout)

    def close(self):
        self.closed = True


class ReceiveDataTests(unittest.TestCase):
    def test_receive_data_waits_for_crlf_split_between_bytes(self):
        connection = FakeSocket((b'1\r', b'\n'))

        self.assertEqual(receive_data(connection), ['1', ''])
        self.assertFalse(connection.closed)

    def test_receive_data_preserves_legacy_list_shape_for_coalesced_lines(self):
        connection = FakeSocket((b'1\r\n1.000\r\n',))

        self.assertEqual(receive_data(connection), ['1', '1.000', ''])

    def test_timeout_invalidates_the_socket(self):
        connection = FakeSocket((socket.timeout(),))

        with self.assertRaisesRegex(CognexCommandError, 'Timed out'):
            receive_data(connection)

        self.assertTrue(connection.closed)

        with self.assertRaisesRegex(CognexCommandError, 'no longer usable'):
            receive_data(connection)

    def test_eof_in_the_middle_of_a_line_invalidates_the_socket(self):
        connection = FakeSocket((b'1\r', b''))

        with self.assertRaisesRegex(CognexCommandError, 'closed before a complete response'):
            receive_data(connection)

        self.assertTrue(connection.closed)

    def test_non_ascii_data_invalidates_the_socket(self):
        connection = FakeSocket((b'\xff\r\n',))

        with self.assertRaisesRegex(CognexCommandError, 'non-ASCII'):
            receive_data(connection)

        self.assertTrue(connection.closed)

    def test_oversized_unterminated_response_invalidates_the_socket(self):
        connection = FakeSocket((b'x' * (_MAX_BUFFERED_BYTES + 1),))

        with self.assertRaisesRegex(CognexCommandError, 'maximum buffered size'):
            receive_data(connection)

        self.assertTrue(connection.closed)

    def test_extra_data_after_a_complete_response_invalidates_the_socket(self):
        connection = FakeSocket((b'1\r\nunexpected',))

        with self.assertRaisesRegex(CognexCommandError, 'remained after the response'):
            _receive_status_response(connection)

        self.assertTrue(connection.closed)

    def test_buffered_partial_data_prevents_the_next_command(self):
        connection = FakeSocket((b'1\r\npartial',))
        self.assertEqual(receive_data(connection), ['1', ''])

        with self.assertRaisesRegex(CognexCommandError, 'pending before a command'):
            send_command(connection, 'GO')

        self.assertTrue(connection.closed)

    def test_pending_kernel_data_prevents_a_new_command(self):
        client, server = socket.socketpair()
        self.addCleanup(server.close)
        server.sendall(b'stale')

        with self.assertRaisesRegex(CognexCommandError, 'pending before a command'):
            send_command(client, 'GO')

        self.assertEqual(client.fileno(), -1)


class LoginFramingTests(unittest.TestCase):
    def test_fragmented_and_coalesced_login_prompts(self):
        connection = FakeSocket((
            b'Welcome to In-Sight(TM) IS3808 Session 1\r\nUs',
            b'er: ',
            b'Pass',
            b'word: ',
            b'User Logged In\r',
            b'\n',
        ))

        with patch('CognexNativePy.utils.socket.socket', return_value=connection):
            opened = open_socket('camera.example')
        login_to_cognex_system(opened, 'user', 'password')

        self.assertIs(opened, connection)
        self.assertEqual(connection.connected_to, ('camera.example', 23))
        self.assertEqual(connection.sent, [b'user\r\n', b'password\r\n'])
        self.assertFalse(connection.closed)

    def test_connection_timeout_closes_the_socket(self):
        connection = FakeSocket(connect_error=socket.timeout())

        with patch('CognexNativePy.utils.socket.socket', return_value=connection):
            with self.assertRaisesRegex(CognexCommandError, 'Connection attempt .* timed out'):
                open_socket('camera.example')

        self.assertTrue(connection.closed)


class CommandFramingTests(unittest.TestCase):
    def test_get_value_reads_fragmented_status_and_value(self):
        connection = FakeSocket((b'1\r\n', b'1.000\r\n'))
        settings = SettingsAndCellsValues(connection)

        self.assertEqual(settings.get_value('ExampleTag'), '1.000')
        self.assertEqual(connection.sent, [b'GVExampleTag\r\n'])

    def test_get_value_handles_crlf_fragmentation_and_next_command(self):
        connection = FakeSocket((
            b'1\r', b'\n1.000\r', b'\n',
            b'1\r\n2.000\r\n',
        ))
        settings = SettingsAndCellsValues(connection)

        self.assertEqual(settings.get_value('FirstTag'), '1.000')
        self.assertEqual(settings.get_value('SecondTag'), '2.000')
        self.assertFalse(connection.closed)

    def test_get_value_keeps_an_explicit_empty_value(self):
        connection = FakeSocket((b'1\r\n\r\n',))

        self.assertEqual(SettingsAndCellsValues(connection).get_value('ExampleTag'), '')

    def test_get_value_error_does_not_wait_for_a_value(self):
        connection = FakeSocket((b'-1\r\n',))

        with self.assertRaisesRegex(CognexCommandError, 'cell ID or symbolic tag is invalid'):
            SettingsAndCellsValues(connection).get_value('ExampleTag')

        self.assertFalse(connection.closed)

    def test_get_file_and_get_job_read_their_second_line(self):
        file_socket = FakeSocket((b'1\r\n', b'Example.job\r\n'))
        job_socket = FakeSocket((b'1\r', b'\n42\r\n'))

        self.assertEqual(FileAndJob(file_socket).get_file(), 'Example.job')
        self.assertEqual(FileAndJob(job_socket).get_job(), 42)

    def test_get_info_reads_all_five_information_lines(self):
        connection = FakeSocket((
            b'1\r\nSerial Number: 123\r',
            b'\nApplication Version: 1.2\r\nMonitor Version: 3.4\r\n',
            b'MAC Address: 00-00-00-00-00-00\r\nDate of Build: Today\r\n',
        ))

        result = SettingsAndCellsValues(connection).get_info()

        self.assertEqual(result['Serial Number'], '123')
        self.assertEqual(result['Application Version'], '1.2')
        self.assertEqual(result['Monitor Version'], '3.4')
        self.assertEqual(result['MAC Address'], '00-00-00-00-00-00')
        self.assertEqual(result['Date of Build'], 'Today')

    def test_set_event_reads_a_fragmented_sized_payload(self):
        connection = FakeSocket((
            b'1\r\n8\r\n<r>',
            b'1</r>\r',
            b'\n',
        ))

        result = ExecutionAndOnline(connection).set_event(0)

        self.assertEqual(result, ('1', '<r>1</r>'))

    def test_set_event_preserves_command_errors(self):
        connection = FakeSocket((b'0\r\n',))

        with self.assertRaisesRegex(CognexCommandError, 'Unrecognized command'):
            ExecutionAndOnline(connection).set_event(0)

        self.assertFalse(connection.closed)

    def test_set_event_rejects_a_negative_payload_size(self):
        connection = FakeSocket((b'1\r\n-1\r\n',))

        with self.assertRaisesRegex(CognexCommandError, 'invalid payload size'):
            ExecutionAndOnline(connection).set_event(0)

        self.assertTrue(connection.closed)

    def test_one_deadline_is_shared_by_a_fragmented_response(self):
        connection = FakeSocket((b'1\r\n', b'value\r\n'))

        with patch('CognexNativePy.utils.time.monotonic', side_effect=(100.0, 101.0, 105.0)):
            response = _receive_status_response(connection, successful_value_lines=1)

        self.assertEqual(response, ['1', 'value'])
        self.assertEqual(
            [timeout for timeout in connection.timeout_history if timeout is not None],
            [29.0, 25.0],
        )

    def test_single_line_status_command_accepts_fragmented_crlf(self):
        connection = FakeSocket((b'1\r', b'\n'))

        self.assertIsNone(SettingsAndCellsValues(connection).set_integer_value('Tag', 10))


class PublicApiTests(unittest.TestCase):
    def test_public_function_signatures_are_unchanged(self):
        self.assertEqual(list(inspect.signature(receive_data).parameters), ['socket'])
        self.assertEqual(list(inspect.signature(open_socket).parameters), ['host_adress'])
        self.assertEqual(
            list(inspect.signature(login_to_cognex_system).parameters),
            ['socket', 'user', 'password'],
        )


if __name__ == '__main__':
    unittest.main()
