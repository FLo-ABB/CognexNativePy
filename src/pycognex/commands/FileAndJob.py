import os

from pycognex.CognexCommandError import CognexCommandError
from pycognex.utils import format_job_data, hex_to_bytes, send_command, receive_data


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
        status_code = receive_data(self.socket)
        print("aaaa")
        print(status_code)
        status_messages = {
            "0": "Unrecognized command.",
            "-1": "The filename is missing.",
            "-2": "The job failed to load, the vision system is Online, or the file was not found.",
            "-4": "The vision system is out of memory.",
            "-6": "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }

        try:
            if status_code == "1":
                return None
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error loading file: {e}")
            return None

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
        if not filename.endswith(".JOB"):
            raise ValueError("The filename must have a .JOB extension.")

        command = f"TF[{filename}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The filename is missing.",
            -2: "The job failed to save, the vision system is Online or the file was not found, therefore the command could not be executed.",
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
            print(f"Error storing file: {e}")
            return None

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
        command = f"RF[{filename}]"
        status_code, job_data = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The job filename is missing.",
            -2: "There is no job saved with the given name or the job data is invalid, therefore the command could not be executed.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation."
        }

        try:
            if status_code == 1:
                lines = job_data.strip().split("\n")
                if len(lines) < 4:
                    raise CognexCommandError("Invalid job data format.")

                job_name = lines[0]
                job_size = int(lines[1])
                job_data_lines = lines[2:-1]
                job_data_hex = "".join(job_data_lines).replace(" ", "")
                job_data_bytes = hex_to_bytes(job_data_hex)
                job_checksum = lines[-1]

                return {
                    "name": job_name,
                    "size": job_size,
                    "data": job_data_bytes,
                    "checksum": job_checksum
                }
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error reading file: {e}")
            return None

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
        formatted_data = format_job_data(data)
        command = f"WF[{filename}][{size}][{formatted_data}][{checksum}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -2: "The job could not be written, or the job data is invalid.",
            -3: "The checksum failed. The checksum does not match the job data.",
            -4: "The In-Sight vision system is out of memory.",
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
            print(f"Error writing file: {e}")
            return None

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
        if not filename.endswith((".JOB", ".CXD")):
            raise ValueError("The filename must have a .JOB or .CXD extension.")

        folder, file_ext = os.path.splitext(filename)
        if folder:
            folder += "/"
        command = f"DF{folder}{file_ext[:-1]}[{filename}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The filename is missing.",
            -2: "The file could not be deleted, the vision system is Online, a file does not exist with the given name, or the job data is invalid,"
                "therefore the command could not be executed.",
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
            print(f"Error deleting file: {e}")
            return None

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
        status_code, filename = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -2: "The active job has not been saved, therefore the command could not be executed.",
        }

        try:
            if status_code == 1:
                return filename
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error getting file: {e}")
            return None

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

        command = f"SJ[{job_id}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The ID is less than 0, or is not an integer.",
            -2: "The job failed to load, the sensor is Online or the file was not found, therefore the command could not be executed.",
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
            print(f"Error setting job: {e}")
            return None

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

        command = f"TJ[{job_id}][{job_name}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The job ID number is invalid or it is not an integer.",
            -2: "The sensor is Online, therefore the command could not be executed.",
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
            print(f"Error storing job: {e}")
            return None

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

        command = f"RJ[{job_id}]"
        status_code, job_data = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The job ID number is outside the allowable range (0 to 999).",
            -2: "The job could not be read, or the job slot is empty, therefore the command could not be executed.",
            -4: "The In-Sight sensor is out of memory.",
            -6: "User does not have Full Access to execute the command. For more information, see Cognex Documentation.",
        }

        try:
            if status_code == 1:
                job_data_lines = job_data.strip().split("\n")
                if len(job_data_lines) < 4:
                    raise CognexCommandError("Invalid job data format.")

                job_name = job_data_lines[0]
                job_size = int(job_data_lines[1])
                job_data_hex = "".join(job_data_lines[2:-1]).replace(" ", "")
                job_data_bytes = hex_to_bytes(job_data_hex)
                job_checksum = job_data_lines[-1]

                return {
                    "name": job_name,
                    "size": job_size,
                    "data": job_data_bytes,
                    "checksum": job_checksum,
                }
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error reading job: {e}")
            return None

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

        job_data_hex = format_job_data(job_data)
        command = f"WJ[{job_id}][{job_name}][{job_size}][{job_data_hex}][{job_checksum}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The job ID number is outside the allowable range (0 to 999).",
            -2: "The job could not be written, or the job data is invalid.",
            -3: "The checksum failed. The checksum does not match the job data.",
            -4: "The In-Sight vision system is out of memory.",
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
            print(f"Error writing job: {e}")
            return None

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

        command = f"DJ[{job_id}]"
        status_code = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -1: "The job ID number is outside the allowable range (0 to 999).",
            -2: "The job could not be deleted, the sensor is Online, or the job slot is empty, therefore the command could not be executed.",
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
            print(f"Error deleting job: {e}")
            return None

    def get_job(self) -> int:
        """
        Returns the ID of the active job on the In-Sight sensor.

        Returns:
            int: The job ID.

        Raises:
            CognexCommandError: If the command to retrieve the job ID fails.

        """
        command = "GJ"
        status_code, job_id = send_command(self.socket, command)

        status_messages = {
            0: "Unrecognized command.",
            -2: "The active job has not been saved or does not have a numerical prefix, therefore the command could not be executed.",
        }

        try:
            if status_code == 1:
                return job_id
            elif status_code in status_messages:
                raise CognexCommandError(status_messages[status_code])
            else:
                raise CognexCommandError(f"Unknown status code: {status_code}")
        except CognexCommandError as e:
            print(f"Error getting job: {e}")
            return None
