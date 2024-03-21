from pycognex import NativeInterface


def main():
    try:
        # Create a socket connection to the Cognex In-Sight vision system and log in
        native_interface = NativeInterface('192.168.56.1', 'admin', '')
        execution_and_online = native_interface.execution_and_online
        file_and_job = native_interface.file_and_job
        image = native_interface.image
        settings_and_cells_values = native_interface.settings_and_cells_values

        # Load the job if it is not already loaded
        job_name = "1myJob.job"
        if file_and_job.get_file() != job_name:
            if execution_and_online.get_online() == 1:
                execution_and_online.set_online(0)
            file_and_job.load_file(job_name)

        # Set the system online to be able to trigg the camera and get results
        if execution_and_online.get_online() == 0:
            execution_and_online.set_online(1)

        # Get the last image from the camera
        with open('image.bmp', 'wb') as f:
            f.write(image.read_image()["data"])

        # Get the value of the cell B010 (spreadsheet view)
        print(settings_and_cells_values.get_value("B", 10))
        # Get the value of the symbolic tag "Pattern_1.Fixture.X" (EasyBuilder view)
        print(settings_and_cells_values.get_value("Pattern_1.Fixture.X"))
        # Set the value of the cell D019 (spreadsheet view) to 53
        settings_and_cells_values.set_integer_value("D", 19, 53)
        # Set the value of the symbolic tag "Pattern_1.Accept_Threshold" to 52
        settings_and_cells_values.set_integer_value("Pattern_1.Accept_Threshold", 52)
        # Set the value of the symbolic tag "Pattern_1.Horizontal_Offset" to 69.3 (EasyBuilder view)
        settings_and_cells_values.set_float_value("Pattern_1.Horizontal_Offset", 69.3)
        # Set the value of the cell D021 (spreadsheet view) to 69.4
        settings_and_cells_values.set_float_value("D", 21, 69.4)
        # Set the region of the cell A031 (spreadsheet view)
        execution_and_online.set_online(0)
        # Set the region of the symbolic tag "Acquisition.Exposure_Region" (EasyBuilder view)
        settings_and_cells_values.set_region("Acquisition.Exposure_Region", 17.9, 32.9, 125.3, 250.4, 0.0, 0.0)
        # Set the region of the cell A009 (spreadsheet view)
        settings_and_cells_values.set_region("A", 9, 69.69, 32.9, 125.3, 250.4, 0.0, 0.0)
        # Set the string of the cell A034
        settings_and_cells_values.set_string("A", 34, "Hello World")
        execution_and_online.set_online(1)

        # Get the information of the settings and cells values
        print(settings_and_cells_values.get_info())
        # data_received = settings_and_cells_values.read_settings()
        # with open('settings.txt', 'wb') as f:
        #     f.write(data_received["settings"])

        # Close the socket connection
        native_interface.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
