from pycognex import NativeInterface


def main():
    try:
        # Create a socket connection to the Cognex In-Sight vision system and log in
        native_interface = NativeInterface('192.168.103.2', 'admin', '')
        execution_and_online = native_interface.execution_and_online
        file_and_job = native_interface.file_and_job

        # Load the job if it is not already loaded
        if execution_and_online.get_online() == 1:
            execution_and_online.set_online(0)
        if file_and_job.get_file() != "formation.job":
            file_and_job.load_file("formation.job")
        execution_and_online.set_online(1)

        # Set the system online to be able to trigg the camera and get results
        if execution_and_online.get_online() == 0:
            execution_and_online.set_online(1)

        # Close the socket connection
        native_interface.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
