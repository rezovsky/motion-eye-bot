import configparser  # Import configparser for working with configuration files

# Read configuration settings from the 'config.ini' file
config = configparser.ConfigParser()
config.read('config.ini')



def colored_check(text, color):
    import sys
    from termcolor import colored  # Import termcolor for colored console output
    supports_color = sys.stdout.isatty()
    if supports_color:
        return colored(text, color)
    else:
        return text

# Function to get a list of connected cameras
def get_connected_cameras():
    from pygrabber.dshow_graph import FilterGraph
    camera_list = {}

    devices = FilterGraph().get_input_devices()

    for device_index, device_name in enumerate(devices):
        camera_list[device_index] = device_name

    return camera_list

# Iterate through sections and parameters in config.ini
for section in config.sections():
    print(f"Section: {colored_check(section, 'light_yellow')}")
    for key, value in config[section].items():
        if key.lower() == 'camera_index':
            connected_cameras = get_connected_cameras()
            print(colored_check("Available cameras:", 'light_cyan'))
            for index, name in connected_cameras.items():
                if index == int(value):
                    print(colored_check(f"{index}: {name}", 'green'))
                else:
                    print(f"{index}: {name}")

            camera_choice = input(
                f"Enter the index of the camera you want to use (current: {colored_check(value, 'green')}, press Enter to keep unchanged): ")
            if camera_choice.strip() == '':
                config[section][key] = value
            else:
                config[section][key] = camera_choice
        else:
            new_value = input(f"Enter new value for {colored_check(key, 'blue')} (current: {colored_check(value, 'green')}, press Enter to keep unchanged): ")
            if new_value.strip():
                config[section][key] = new_value

# Write the updated values to config.ini with keys in uppercase
with open('config.ini', 'w') as configfile:
    config.write(configfile)

print("Settings updated successfully.")
