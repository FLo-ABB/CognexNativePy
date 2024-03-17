from pycognex import NativeInterface


def main():
    try:
        # Create a socket connection to the Cognex In-Sight vision system and log in
        native_interface = NativeInterface('192.168.103.2', 'admin', '')
        exectution_and_online = native_interface.exectution_and_online
        file_and_job = native_interface.file_and_job

        # Load the job if it is not already loaded
        if exectution_and_online.get_online() == 1:
            exectution_and_online.set_online(0)
        file_and_job.load_file("item1.job")
        exectution_and_online.set_online(1)

        # Set the system online to be able to trigg the camera and get results
        if exectution_and_online.get_online() == 0:
            exectution_and_online.set_online(1)

        # Close the socket connection
        native_interface.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
