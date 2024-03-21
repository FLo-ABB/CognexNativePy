import socket

from CognexNativePy.CognexCommandError import CognexCommandError
from CognexNativePy.utils import send_command, receive_data


class ExecutionAndOnline:
    def __init__(self, socket: socket.socket):
        self.socket = socket

    def set_online(self, mode: int) -> None:
        """
        Sets the In-Sight sensor into Online or Offline mode. For more information, see Online/Offline.
        Note:
            - This command cannot place the In-Sight sensor into Online mode if the sensor has been set Offline either manually
              in the In-Sight Explorer user interface or by a Discrete Input signal.
            - The In-Sight Explorer application will send Set Online commands to In-Sight sensors to perform administrative functions
              such as Backup andRestore.

        Args:
            mode (int): "0" for Offline, "1" for Online.

        Returns:
            None

        Raises:
            ValueError: If the mode is not "0" or "1".
            CognexCommandError: If the command to set the Online mode fails.
        """
        if mode not in [0, 1]:
            raise ValueError("The mode must be 0 for Offline or 1 for Online.")
        else:
            command = f"SO{mode}"
            send_command(self.socket, command)
            status_code = receive_data(self.socket)[0]
            status_messages = {
                "0": "Unrecognized command.",
                "-1": "The value given for Int is either out of range, or is not a valid integer.",
                "-2": "The command could not be executed.",
                "-5": ("The communications flag was successful but the sensor did not go Online because "
                       "the sensor is set Offline manually through the In-Sight Explorer user interface "
                       "or by a Discrete I/O signal."),
                "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
            }

            if status_code == "1":
                return None
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_online(self) -> int:
        """
        Returns the Online state of the In-Sight vision system. For more information, see Online/Offline.

        Returns:
            int: The Online state of the vision system ("0" for Offline, "1" for Online).

        Raises:
            CognexCommandError: If the command to retrieve the Online state fails.
        """
        command = "GO"
        send_command(self.socket, command)
        online_state = int(receive_data(self.socket)[0])

        if online_state in [0, 1]:
            return int(online_state)
        else:
            raise CognexCommandError(f"Unknown Online state: {online_state}")

    def set_event(self, event_code: int) -> tuple:
        """
        Triggers a specified event in the spreadsheet through a Native Mode command.

        Notes:
            - If the In-Sight vision system will be configured to accept an acquisition trigger from a PLC/Motion Controller via a Native Mode
              command, Cognex recommends that the SetEvent and Wait function be utilized, with the Event code set to 8 (SW8). This will ensure
              that vision system waits for both the acquisition and inspection to be completed before sending a "complete" response back to the
              PLC/Motion Controller, and that previous inspection results are not being sent to the PLC/Motion Controller. The "complete" response
              from the vision system can also then be used to create conditional PLC logic that sends a read request for the inspection results.
              For more information, see Set Event and Wait.
            - If the SetEvent function will be used by a PLC/Motion Controller to trigger an acquisition, it should only be used in circumstances
              where the inspection results are not also being read. Otherwise, the acquisition and inspection will not be synchronized, with the
              vision system returning a response as soon as the image is acquired and before the inspection has been completed.
            - In job deployment environments where In-Sight Explorer or the VisionView application are monitoring inspections, if the job depends
              on a Soft Event (e.g., configured as a Timer function) to trigger a spreadsheet event, it may cause the inspection of an image to be
              delayed if it is triggered shortly before the acquisition cycle completes. If the job file is large (i.e., it contains many Vision
              Tools, such as Pattern Match, Flaw Detection or InspectEdge tools, in addition to other job logic), the update required by In-Sight
              Explorer or VisionView may prevent an image from being inspected until the display update is queued. For applications that require
              exact timing (e.g., measured in the 10s of milliseconds), this update might delay the determination of pass/fail results and the
              transmission of results to the next station (e.g., a PLC or motion controller) in the inspection process. To avoid delayed inspections
              in these application environments, Cognex recommends Soft Events not be used.

        Args:
            event_code (int): The Event code to set.
                            0 to 7 = Specifies a soft trigger (Soft 0, Soft 1, ... Soft 7).
                            8 = Acquire an image and update the spreadsheet. This option requires the AcquireImage function's Trigger parameter to
                            be set to External, Manual or Network.

        Returns:
            tuple: A tuple containing the status code and the result in XML format.

        Raises:
            ValueError: If the event code is not between 0 and 8 (inclusive).
            CognexCommandError: If the command to trigger the event fails.
        """
        if not 0 <= event_code <= 8:
            raise ValueError("The event code must be between 0 and 8 (inclusive).")

        command = f"SE{event_code}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code, result = data_received[0], data_received[1]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The number is either out of range (0 to 8) or not an integer.",
            "-2": "The command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return status_code, result
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_event_and_wait(self, event_code: int) -> None:
        """
        Triggers a specified event and waits until the command is completed to return a response.

        Notes:
            - The In-Sight vision system must be Online.
            - If the In-Sight vision system will be configured to accept an acquisition trigger from a PLC/Motion Controller via a Native
              Mode command, Cognex recommends that the SetEvent and Wait function be utilized, with the Event code set to 8 (SW8). This
              will ensure that vision system waits for both the acquisition and inspection to be completed before sending a "complete"
              response back to the PLC/Motion Controller, and that previous inspection results are not being sent to the PLC/Motion Controller.
              The "complete" response from the vision system can also then be used to create conditional PLC logic that sends a read request
              for the inspection results.

        Args:
            event_code (int): The Event code to set.
                            0 to 7 = Specifies a soft trigger (Soft 0, Soft 1, ... Soft 7).
                            8 = Acquire an image and update the spreadsheet. This option requires the AcquireImage function's Trigger parameter to be
                            set to External, Manual or Network.

        Returns:
            str: The status code.

        Raises:
            ValueError: If the event code is not between 0 and 8 (inclusive).
            CognexCommandError: If the command to trigger the event fails.
        """
        if not 0 <= event_code <= 8:
            raise ValueError("The event code must be between 0 and 8 (inclusive).")

        command = f"SW{event_code}"
        send_command(self.socket, command)

        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The number is either out of range (0 to 8) or not an integer.",
            "-2": "The command could not be executed, or the sensor is Offline.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def reset_system(self) -> None:
        """
        Resets the In-Sight sensor. This command is similar to physically cycling power on the sensor.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to reset the system fails.
        """
        command = "RT"
        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code is None:
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def send_message(self, message: str, event_code: int = None) -> None:
        """
        Sends a string to an In-Sight spreadsheet over a Native Mode connection, and optionally, triggers a spreadsheet Event.

        Args:
            message (str): The string to set. The string must be enclosed with quotation marks.
            event_code (int, optional): The Event code to set. This is an optional parameter.
                                        0 to 7: Specifies a soft trigger (Soft 0, Soft 1, ... , Soft 7).
                                        8: Acquire an image and update the spreadsheet. This option requires that the AcquireImage function's
                                        Trigger parameter be set to External or Manual.

        Returns:
            int: The status code.

        Raises:
            CognexCommandError: If the command to send the message fails.
        """
        if event_code is not None and (not 0 <= event_code <= 8):
            raise ValueError("The event code must be between 0 and 8 (inclusive).")

        command = f'SM"{message}"'
        if event_code is not None:
            command += f'{event_code}'

        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The number is either out of range (0 to 8) or not an integer.",
            "-2": "The command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")
