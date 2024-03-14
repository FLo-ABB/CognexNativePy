from CognexCommandError import CognexCommandError
from utils import send_command


def set_online(mode: int) -> None:
    """
    Sets the In-Sight sensor into Online or Offline mode. For more information, see Online/Offline.
    Note:
        - This command cannot place the In-Sight sensor into Online mode if the sensor has been set Offline either manually in the In-Sight Explorer
          user interface or by a Discrete Input signal.
        - The In-Sight Explorer application will send Set Online commands to In-Sight sensors to perform administrative functions such as Backup and
          Restore.

    Args:
        mode (int): 0 for Offline, 1 for Online.

    Returns:
        None

    Raises:
        ValueError: If the mode is not 0 or 1.
        CognexCommandError: If the command to set the Online mode fails.

    """
    if mode not in [0, 1]:
        raise ValueError("The mode must be 0 for Offline or 1 for Online.")

    command = f"SO[{mode}]"
    status_code = send_command(command)

    status_messages = {
        0: "Unrecognized command.",
        -1: "The value given for Int is either out of range, or is not a valid integer.",
        -2: "The command could not be executed.",
        -5: ("The communications flag was successful but the sensor did not go Online because "
             "the sensor is set Offline manually through the In-Sight Explorer user interface "
             "or by a Discrete I/O signal."),
        -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
    }

    try:
        if status_code == 1:
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")
    except CognexCommandError as e:
        print(f"Error setting Online mode: {e}")
        return None


def get_online() -> int:
    """
    Returns the Online state of the In-Sight vision system. For more information, see Online/Offline.

    Returns:
        int: The Online state of the vision system (0 for Offline, 1 for Online).

    Raises:
        CognexCommandError: If the command to retrieve the Online state fails.

    """
    command = "GO"
    online_state = send_command(command)

    try:
        if online_state in [0, 1]:
            return online_state
        else:
            raise CognexCommandError(f"Unknown Online state: {online_state}")
    except CognexCommandError as e:
        print(f"Error getting Online state: {e}")
        return None
