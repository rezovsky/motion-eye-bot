# Motion eye bot


This is a small script that monitors motion from your webcam and sends you images and videos via a Telegram bot if motion is detected. To use it, you need to register a bot on Telegram and also know your Telegram ID (which you can obtain from the @userinfobot).

## Installation

1. Clone the repository.
2a. Run `install.bat` to automatically set up venv, install dependencies, and perform initial program configuration (be sure to specify your Telegram bot token, your Telegram ID for receiving messages, and choose a camera; you can leave other parameters at their default values).
2b. Set up a virtual environment and manually install dependencies from the requirements.txt file. Modify the settings in the config.ini file or by using the `settings.py` script.

## Usage

Option 1: Launch using `start.bat`. 
Option 2: Launch the `main.py` script.

## Settings

[BotSettings]

`token` - Your Telegram bot token from `@BotFather`

`chat_id` - Your Telegram ID (You can obtain it from `@userinfobot`)

`time_to_first_photo` - Number of seconds to delay before sending the first photo upon motion detection

`time_to_next_photo` - Number of seconds to wait before sending subsequent photos if motion continues

`time_to_send_videos` - Delay before sending a video after motion has stopped; if motion resumes before this time elapses, recording will continue

[MotionDetectionSettings]

`threshold_area` - Size of the detected object area, depending on script usage; smaller values detect smaller objects (e.g., a human face in a laptop camera frame is roughly 40000)

`frame_rate` - Number of frames per second in the recorded video

`camera_index` - Camera number in the system; default is 0 and depends on the number of connected cameras

`windows_visible` controls whether to display a window with a view from the camera. The default value is 1, which is used to set up the camera's position or view the image coverage.
