import time  # Import the time module for time-related operations
import aiohttp  # Import aiohttp for asynchronous HTTP requests
import cv2  # Import OpenCV for image and video processing
import asyncio  # Import asyncio for asynchronous programming
from aiogram import Bot, types  # Import aiogram for Telegram bot functionality
import configparser  # Import configparser for working with configuration files

# Read configuration settings from the 'config.ini' file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve Telegram bot token and chat ID from the configuration
TOKEN = config['BotSettings']['TOKEN']
CHAT_ID = config['BotSettings']['CHAT_ID']

# Create a bot instance using the retrieved token
bot = Bot(token=TOKEN)

# Function to perform motion detection on a frame
def motion_detection(frame, motion_detector, threshold_area):
    global frame_count
    fg_mask = motion_detector.apply(frame)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > threshold_area:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a bounding box around the object
            motion_detected = True

    return frame, motion_detected

# Asynchronous function to send a motion photo to Telegram
async def send_motion_photo(session):
    print('Sending photo...')
    async with session:
        with open('motion_photo.jpg', 'rb') as photo:
            await bot.send_photo(chat_id=CHAT_ID, photo=types.InputFile(photo))

# Asynchronous function to send a motion video to Telegram
async def send_motion_video(session):
    print('Sending video...')
    async with session:
        with open('motion_detected.mp4', 'rb') as video:
            await bot.send_video(chat_id=CHAT_ID, video=types.InputFile(video))

# Asynchronous main function
async def main():
    cap = cv2.VideoCapture(int(config['MotionDetectionSettings']['camera_index']))
    motion_detector = cv2.createBackgroundSubtractorMOG2()
    threshold_area = int(config['MotionDetectionSettings']['threshold_area'])

    async with aiohttp.ClientSession() as session:
        recording = False
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        detect_time = time.time()
        not_detect_time = time.time()

        # Configuration settings for time intervals
        second_first_photo = int(config['BotSettings']['time_to_first_photo'])
        seconds_next_photo = int(config['BotSettings']['time_to_next_photo'])
        seconds_to_send_videos = int(config['BotSettings']['time_to_send_videos'])
        frame_rate = int(config['MotionDetectionSettings']['frame_rate'])
        windows_visible = bool(int(config['MotionDetectionSettings']['windows_visible']))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result_frame, motion_detected = motion_detection(frame, motion_detector, threshold_area)

            if motion_detected:
                detect_time = time.time()
                times = abs(not_detect_time - detect_time)

                # Logic for sending motion photos based on time intervals
                if second_first_photo < times < second_first_photo + 1:
                    cv2.imwrite('motion_photo.jpg', result_frame)
                    await send_motion_photo(session)

                if times >= seconds_next_photo + second_first_photo + 1:
                    cv2.imwrite('motion_photo.jpg', result_frame)
                    not_detect_time = time.time() - second_first_photo - 1
                    await send_motion_photo(session)

                if not recording:
                    recording = True
                    out = cv2.VideoWriter('motion_detected.mp4', fourcc, frame_rate, (640, 480))

                out.write(frame)
            else:
                not_detect_time = time.time()
                times = abs(not_detect_time - detect_time)

                # Logic for sending motion videos based on time intervals
                if times >= seconds_to_send_videos and recording:
                    recording = False
                    out.release()
                    await send_motion_video(session)

            if windows_visible:
                cv2.imshow('Motion Detection', result_frame)

            if cv2.waitKey(30) & 0xFF == 27:
                break

        if out:
            out.release()

        cap.release()
        cv2.destroyAllWindows()

        await session.close()

if __name__ == "__main__":
    asyncio.run(main())  # Run the asynchronous main function
