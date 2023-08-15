import cv2
import configparser
from termcolor import colored
from pygrabber.dshow_graph import FilterGraph

# Чтение настроек из конфигурационного файла
config = configparser.ConfigParser()
config.read('config.ini')


# Вывод списка доступных камер
def get_connected_cameras():
    camera_list = {}

    devices = FilterGraph().get_input_devices()

    for device_index, device_name in enumerate(devices):
        camera_list[device_index] = device_name

    return camera_list

# Проходимся по разделам и параметрам в config.ini
for section in config.sections():
    print(f"Section: {colored(section, 'light_yellow')}")
    for key, value in config[section].items():
        if key.lower() == 'camera_index':
            connected_cameras = get_connected_cameras()
            print(colored("Available cameras:", 'light_cyan'))
            for index, name in connected_cameras.items():
                if index == int(value):
                    print(colored(f"{index}: {name}", 'green'))
                else:
                    print(f"{index}: {name}")

            camera_choice = input(
                f"Enter the index of the camera you want to use (current: {colored(value, 'green')}, press Enter to keep unchanged): ")
            if camera_choice.strip() == '':
                config[section][key] = value
            else:
                config[section][key] = camera_choice
        else:
            new_value = input(f"Enter new value for {colored(key, 'blue')} (current: {colored(value, 'green')}, press Enter to keep unchanged): ")
            if new_value.strip():
                config[section][key] = new_value

# Записываем обновленные значения в config.ini с ключами в верхнем регистре
with open('config.ini', 'w') as configfile:
    config.write(configfile)

print("Settings updated successfully.")
