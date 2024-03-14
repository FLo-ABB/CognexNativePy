from CognexCommandError import CognexCommandError
from utils import hex_to_bytes, send_command


def load_file(filename: str) -> None:
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
    command = f"LF[{filename}]"
    status_code = send_command(command)

    status_messages = {
        0: "Unrecognized command.",
        -1: "The filename is missing.",
        -2: "The job failed to load, the vision system is Online, or the file was not found.",
        -4: "The vision system is out of memory.",
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
        print(f"Error loading file: {e}")
        return None


def store_file(filename: str) -> None:
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
    status_code = send_command(command)

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


def read_file(filename: str) -> dict:
    """
    Reads a job from the specified In-Sight flash memory, RAM Disk or SD Card.
    Note:
        - To read a job file stored in the RAMDisk folder, the syntax is: RFRAMDisk/[Filename].
          For example, to read the file "Model.job" stored in the vision system's RAMDisk folder, issue the following command: "RFRAMDisk/Model.job".
        - To read a job file stored in the SD Card folder, the syntax is RFSDCARD/[Filename].
          For example, to read the file "Model.job" stored in the vision system's SD Card folder, issue the following command: "RFSDCARD/Model.job".

    Args:
        filename (str): The name of the file to read.

    Returns:
        dict: A dictionary containing the job data.

    Raises:
        CognexCommandError: If the command to read the file fails.

    """
    command = f"RF[{filename}]"
    status_code, job_data = send_command(command)

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
