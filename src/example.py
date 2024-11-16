from CognexNativePy import NativeInterface, utils


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

        # Get the last image from the camera and save it as a BMP file
        image_dic = image.read_image()
        with open('image.bmp', 'wb') as f:
            f.write(image_dic["data"])
        print(f"Checksum from cognex camera: {image_dic['checksum']}")
        print(f"Checksum calculated: {utils.calculate_checksum(image_dic["data"])}")

        # Get the value of the cell B010 (spreadsheet view)
        print(settings_and_cells_values.get_value("B", 10))
        # Set the value of the cell D019 (spreadsheet view) to 53
        settings_and_cells_values.set_integer_value("D", 19, 53)
        # Set the value of the symbolic tag "Pattern_1.Horizontal_Offset" to 69.3 (EasyBuilder view)
        settings_and_cells_values.set_float_value("Pattern_1.Horizontal_Offset", 69.3)
        # Get the information of the settings and cells values
        print(settings_and_cells_values.get_info())

        # Close the socket connection
        native_interface.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
