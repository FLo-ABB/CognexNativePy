from CognexNativePy.CognexCommandError import CognexCommandError
from CognexNativePy.utils import (format_data, receive_data,
                                  receive_data_from_socket, send_command)


class FileAndJob:
    def __init__(self, socket):
        self.socket = socket

    def load_file(self, filename: str) -> None:
        """
        Loads the specified job from flash memory on the In-Sight vision system, RAM Disk or SD Card, making it the active job.
        Note:
            - The In-Sight vision system must be Offline.
            - To load a job file stored in the RAMDisk folder, the syntax is: LFRAMDisk/[Filename].
            For example, to load the file "Product.job" stored in the vision system's RAMDisk folder, issue the following command:
            "LFRAMDisk/Product.job".
            - To load a job file stored in the SD Card folder, the syntax is LFSDCARD/[Filename].
            For example, to read the file "Product.job" stored in the vision system's SD Card folder, issue the following command:
            "LFSDCARD/Product.job".
            - The Job Server Settings dialog can be used to configure an FTP server that will host In-Sight job files for the In-Sight vision system,
            which allows another device, such as a PLC or robot controller via the LF and TF Native Mode commands, to change jobs without specifying
            a location.

        Args:
            filename (str): The name of the file to load.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to load the file fails.

        """
        command = f"LF{filename}"
        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The filename is missing.",
            "-2": "The job failed to load, the vision system is Online, or the file was not found.",
            "-4": "The vision system is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def store_file(self, filename: str) -> None:
        """
        Saves the current job in flash memory on the In-Sight vision system, RAM Disk or SD Card.
        Note:
            - If the Allow Online Job Save checkbox is enabled, users with Full or Protected access are allowed to save jobs while Online.
            If the Allow Online Job Save checkbox is not enabled, the vision system must be Offline to save jobs.
            - To save the current job file, with the specified filename, to the vision system's RAMDisk folder, the syntax is: TFRAMDisk/[Filename].
            For example, to save the file "Test.job" to the vision system's RAMDisk folder, issue the following command: "TFRAMDisk/Test.job".
            - To save the current job file, with the specified file name, to the vision system's SD Card folder, the syntax is TFSDCARD/[Filename].
            For example, to save the file "Test.job" stored to the vision system's SD Card folder, issue the following command: "TFSDCARD/Test.job".
            - The Job Server Settings dialog is used to configure an FTP server that will host In-Sight job files for the In-Sight vision system,
            which allows another device, such as a PLC or robot controller via the LF and TF Native Mode commands, to change jobs without specifying
            a location.

        Args:
            filename (str): The name of the file to save, including the .JOB extension.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to save the file fails.

        """
        if not filename.upper().endswith(".JOB"):
            raise ValueError("The filename must have a .JOB extension.")
        else:
            command = f"TF{filename}"
            send_command(self.socket, command)
            status_code = receive_data(self.socket)[0]

            status_messages = {
                "0": "Unrecognized command.",
                "-1": "The filename is missing.",
                "-2": "The job failed to save, the vision system is Online or the file was not found, therefore the command could not be executed.",
                "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
            }

            if status_code == "1":
                return None
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")

    def read_file(self, filename: str) -> dict:
        """
        Reads a job from the specified In-Sight flash memory, RAM Disk or SD Card.
        Note:
            - To read a job file stored in the RAMDisk folder, the syntax is: RFRAMDisk/[Filename].
            For example, to read the file "Model.job" stored in the vision system's RAMDisk folder, issue the following command:
            "RFRAMDisk/Model.job".
            - To read a job file stored in the SD Card folder, the syntax is RFSDCARD/[Filename].
            For example, to read the file "Model.job" stored in the vision system's SD Card folder, issue the following command:
            "RFSDCARD/Model.job".

        Args:
            filename (str): The name of the file to read.

        Returns:
            dict: A dictionary containing the job data.

        Raises:
            CognexCommandError: If the command to read the file fails.

        """
        command = f"RF{filename}"
        send_command(self.socket, command)
        data_received = receive_data_from_socket(self.socket, 'file')
        status_code = data_received["status_code"]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The job filename is missing.",
            "-2": "There is no job saved with the given name or the job data is invalid, therefore the command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }
        if status_code == "1":
            return {
                "name": data_received["file_name"],
                "size": data_received["size"],
                "data": data_received["data"],
                "checksum": data_received["checksum"]
            }
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def write_file(self, filename: str, size: int, data: bytes, checksum: str) -> None:
        """
        Sends a job to the flash memory on the In-Sight vision system, RAM Disk or SD Card.
        Note:
            - The In-Sight vision system must be Offline.
            - To send a job file stored in the vision system's RAMDisk folder, the filename must include the RAMDisk folder path.
            For example, "RAMDisk/NewModel.job".
            - To send a job file stored in the vision system's SD Card folder, the filename must include the SD Card folder path.
            For example, "SDCARD/NewModel.job".

        Args:
            filename (str): The name of the job.
            size (int): The size (in bytes) of the job.
            data (bytes): The actual job data.
            checksum (str): Four ASCII hexadecimal bytes that are a checksum of the job data.

        Returns:
            None

        Raises:
            CognexCommandError: If the command to write the file fails.
        """
        send_command(self.socket, "WF")
        send_command(self.socket, f"{filename}")
        send_command(self.socket, f"{size}")
        send_command(self.socket, f"{format_data(data)}")
        send_command(self.socket, f"{checksum}")

        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The job could not be written, or the job data is invalid.",
            "-3": "The checksum failed. The checksum does not match the job data.",
            "-4": "The In-Sight vision system is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def delete_file(self, filename: str) -> None:
        """
        Deletes a job or .CXD file from the In-Sight vision system's RAMDisk or SD Card folders.
        Note:
            - The In-Sight vision system must be Offline.
            - To delete a job or .CXD file stored in the vision system's RAMDisk folder, the syntax is: DFRAMDisk/[Filename].
            For example, to delete the file "Test.job" stored in the vision system's RAMDisk folder, issue the following command:
            "DFRAMDisk/Test.job".
            - To delete a job or .CXD file stored in the vision system's SD Card folder, the syntax is: DFSDCARD/[Filename].
            For example, to delete the file "Test.job" stored in the vision system's SD Card folder, issue the following command:
            "DFSDCARD/Test.job".

        Args:
            filename (str): The name of the file to delete, including the .JOB or .CXD extension.

        Returns:
            None

        Raises:
            ValueError: If the filename does not have a .JOB or .CXD extension.
            CognexCommandError: If the command to delete the file fails.

        """
        if not filename.upper().endswith((".JOB", ".CXD")):
            raise ValueError("The filename must have a .JOB or .CXD extension.")
        command = f"DF{filename}"
        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The filename is missing.",
            "-2": "The file could not be deleted, the vision system is Online, a file does not exist with the given name, or the job data is invalid,"
            "therefore the command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_file(self) -> str:
        """
        Returns the filename of the active job on the In-Sight vision system, RAM Disk or SD Card.
        Note:
            - The active job must be saved before this command can be executed successfully.
            - If the active job is saved to the vision system's RAMDisk folder, the Get File output includes the RAMDisk folder path.
            For example, if the active job, "Test.job", is saved in the vision system's RAMDisk folder, the Get File command returns
            "RAMDisk/Test.job".
            - If the active job is saved to the vision system's SD Card folder, the Get File output includes the SD Card folder path.
            For example, if the active job, "Test.job", is saved in the vision system's SD Card folder, the Get File command returns
            "SDCARD/Test.job".

        Returns:
            str: The name of the file.

        Raises:
            CognexCommandError: If the command to retrieve the filename fails.

        """
        command = "GF"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code, filename = data_received[0], data_received[1]
        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The active job has not been saved, therefore the command could not be executed.",
        }

        if status_code == "1":
            return filename
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def set_job(self, job_id: int) -> None:
        """
        Loads a job from one of the job slots in flash memory on the In-Sight sensor, making it the active job.
        Note:
            - The In-Sight sensor must be Offline.
            - This command only works on a job saved on the flash memory on the In-Sight vision system.
            If the job is stored on the configured Job Server or the SD Card installed to the In-Sight vision system, this command does not work.
            - To use the job ID number feature, the job to be loaded must be saved with a numerical prefix of 0 to 999.

        Args:
            job_id (int): The ID number of the job to load (0 to 999).

        Returns:
            None

        Raises:
            ValueError: If the job ID is not between 0 and 999 (inclusive).
            CognexCommandError: If the command to load the job fails.

        """
        if not 0 <= job_id <= 999:
            raise ValueError("The job ID must be between 0 and 999 (inclusive).")

        command = f"SJ{job_id}"
        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The ID is less than 0, or is not an integer.",
            "-2": "The job failed to load, the sensor is Online or the file was not found, therefore the command could not be executed.",
            "-4": "The In-Sight sensor is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def store_job(self, job_id: int, job_name: str) -> None:
        """
        Saves the current job into the specified slot in flash memory on the In-Sight sensor.
        Note:
            - If the Allow Online Job Save checkbox is enabled, users with Full or Protected access are allowed to save jobs while Online.
            If the Allow Online Job Save checkbox is not enabled, the vision system must be Offline to save jobs.
            - This command only works on a job saved on the flash memory on the In-Sight vision system.
            If the job is stored on the configured Job Server or the SD Card installed to the In-Sight vision system, this command does not work.
            - To use the job ID number feature, the job to be saved must be saved with a numerical prefix of 0 to 999.

        Args:
            job_id (int): The job ID number (0 to 999).
            job_name (str): The name of the job. The command will execute with or without the .JOB file extension.

        Returns:
            None

        Raises:
            ValueError: If the job ID is not between 0 and 999 (inclusive).
            CognexCommandError: If the command to save the job fails.

        """
        if not 0 <= job_id <= 999:
            raise ValueError("The job ID must be between 0 and 999 (inclusive).")

        command = f"TJ{job_id}{job_name}"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The job ID number is invalid or it is not an integer.",
            "-2": "The sensor is Online, therefore the command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def read_job(self, job_id: int) -> dict:
        """
        Reads a job from the specified In-Sight job slot.

        Args:
            job_id (int): The job ID number (0 to 999).

        Returns:
            dict: A dictionary containing the job data.

        Raises:
            ValueError: If the job ID is not between 0 and 999 (inclusive).
            CognexCommandError: If the command to read the job fails.

        """
        if not 0 <= job_id <= 999:
            raise ValueError("The job ID must be between 0 and 999 (inclusive).")

        command = f"RJ{job_id}"
        send_command(self.socket, command)
        data_received = receive_data_from_socket(self.socket, 'job')
        status_code = data_received["status_code"]
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The job ID number is outside the allowable range (0 to 999).",
            "-2": "The job could not be read, or the job slot is empty, therefore the command could not be executed.",
            "-4": "The In-Sight sensor is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }
        if status_code == "1":
            return {
                "id": data_received["file_name"],
                "size": data_received["size"],
                "data": data_received["data"],
                "checksum": data_received["checksum"]
            }
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def write_job(self, job_id: int, job_name: str, job_size: int, job_data: bytes, job_checksum: str) -> None:
        """
        Sends a job to the specified In-Sight job slot in flash memory on the In-Sight sensor.

        Args:
            job_id (int): The job ID number (0 to 999).
            job_name (str): The job name.
            job_size (int): The size, in bytes, of the job.
            job_data (bytes): The actual job data.
            job_checksum (str): Four ASCII hexadecimal bytes that are a checksum of the job data.

        Returns:
            None

        Raises:
            ValueError: If the job ID is not between 0 and 999 (inclusive).
            CognexCommandError: If the command to write the job fails.

        """
        if not 0 <= job_id <= 999:
            raise ValueError("The job ID must be between 0 and 999 (inclusive).")

        send_command(self.socket, f"WJ{job_id}")
        send_command(self.socket, f"{job_name}")
        send_command(self.socket, f"{job_size}")
        send_command(self.socket, f"{format_data(job_data)}")
        send_command(self.socket, f"{job_checksum}")
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The job ID number is outside the allowable range (0 to 999).",
            "-2": "The job could not be written, or the job data is invalid.",
            "-3": "The checksum failed. The checksum does not match the job data.",
            "-4": "The In-Sight vision system is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def delete_job(self, job_id: int) -> None:
        """
        Deletes the job from the specified slot in flash memory on the In-Sight sensor.

        Args:
            job_id (int): The job ID number (0 to 999).

        Returns:
            None

        Raises:
            ValueError: If the job ID is not between 0 and 999 (inclusive).
            CognexCommandError: If the command to delete the job fails.

        """
        if not 0 <= job_id <= 999:
            raise ValueError("The job ID must be between 0 and 999 (inclusive).")

        command = f"DJ{job_id}"
        send_command(self.socket, command)
        status_code = receive_data(self.socket)[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The job ID number is outside the allowable range (0 to 999).",
            "-2": "The job could not be deleted, the sensor is Online, or the job slot is empty, therefore the command could not be executed.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        if status_code == "1":
            return None
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")

    def get_job(self) -> int:
        """
        Returns the ID of the active job on the In-Sight sensor.

        Notes:
            - To use the job ID number feature, the job to be loaded must be saved with a numerical prefix of 0 to 999.
            - The active job must be saved with a numerical prefix before this command can be executed successfully. If the job has been dragged and
              dropped, the file name must have a numerical prefix before this command can be executed successfully.
            - When a Get Job command is issued using Motoman communications, the status data is returned but the result data is not returned. Use the
              Get File command instead of the Get Job command, or place the job ID number in another cell in the spreadsheet and use the Get Value
              command.

        Returns:
            int: The job ID.

        Raises:
            CognexCommandError: If the command to retrieve the job ID fails.

        """
        command = "GJ"
        send_command(self.socket, command)
        data_received = receive_data(self.socket)
        status_code = data_received[0]

        status_messages = {
            "0": "Unrecognized command.",
            "-2": "The active job has not been saved or does not have a numerical prefix, therefore the command could not be executed.",
        }

        if status_code == "1":
            job_id = int(data_received[1])
            return job_id
        elif status_code in status_messages:
            raise CognexCommandError(status_messages[status_code])
        else:
            raise CognexCommandError(f"Unknown status code: {status_code}")
