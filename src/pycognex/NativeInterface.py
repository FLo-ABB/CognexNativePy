from .CognexCommandError import CognexCommandError
from .commands.ExecutionAndOnline import ExecutionAndOnline
from .commands.FileAndJob import FileAndJob
from .commands.Image import Image
from .commands.SettingsAndCellsValues import SettingsAndCellsValues
from .utils import close_socket, login_to_cognex_system, open_socket


class NativeInterface():
    """
    Represents a native interface to interact with a Cognex system.
    When the instance is created, a connection to the Cognex system is established (socket, login).
    4 commands categories are available: execution_and_online, file_and_job, image, settings_and_cells_values.
    See the cognex documentation for more details about the commands.

    Args:
        ip_address (str): The IP address of the Cognex system.
        user (str): The username for authentication.
        password (str): The password for authentication.
    """

    def __init__(self, ip_address: str, user: str, password: str):
        self.ip_address = ip_address
        self.user = user
        self.password = password
        try:
            self.socket = open_socket(ip_address)
            login_to_cognex_system(self.socket, user, password)
        except CognexCommandError as e:
            self.socket = None
            raise e
        self.execution_and_online = ExecutionAndOnline(self.socket)
        self.file_and_job = FileAndJob(self.socket)
        self.image = Image(self.socket)
        self.settings_and_cells_values = SettingsAndCellsValues(self.socket)

    def __del__(self):
        if self.socket is not None:
            close_socket(self.socket)
        else:
            pass

    def close(self):
        """
        Closes the connection to the Cognex system.
        """
        if self.socket is not None:
            close_socket(self.socket)
        else:
            pass
