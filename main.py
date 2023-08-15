import time
import aiohttp
import cv2
import asyncio
from aiogram import Bot, types
import configparser

# Чтение настроек из конфигурационного файла
config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['BotSettings']['TOKEN']
CHAT_ID = config['BotSettings']['CHAT_ID']

bot = Bot(token=TOKEN)


def motion_detection(frame, motion_detector, threshold_area):
    global frame_count
    fg_mask = motion_detector.apply(frame)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > threshold_area:
            print(area)
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Рисуем рамку вокруг объекта
            motion_detected = True

    return frame, motion_detected


async def send_motion_photo(session):
    print('send photo')
    async with session:
        with open('motion_photo.jpg', 'rb') as photo:
            await bot.send_photo(chat_id=CHAT_ID, photo=types.InputFile(photo))


async def send_motion_video(session):
    print('send video')
    async with session:
        with open('motion_detected.mp4', 'rb') as video:
            await bot.send_video(chat_id=CHAT_ID, video=types.InputFile(video))



async def main():
    cap = cv2.VideoCapture(int(config['MotionDetectionSettings']['camera_index']))
    motion_detector = cv2.createBackgroundSubtractorMOG2()
    threshold_area = int(config['MotionDetectionSettings']['threshold_area'])

    # Создать сессию
    async with aiohttp.ClientSession() as session:

        recording = False
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        detect_time = time.time()
        not_detect_time = time.time()

        second_first_photo = int(config['BotSettings']['second_first_photo'])
        seconds_next_photo = int(config['BotSettings']['seconds_next_photo'])
        seconds_to_send_videos = int(config['BotSettings']['seconds_to_send_videos'])
        frame_rate = int(config['MotionDetectionSettings']['frame_rate'])

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result_frame, motion_detected = motion_detection(frame, motion_detector, threshold_area)

            if motion_detected:
                detect_time = time.time()
                times = abs(not_detect_time - detect_time)
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
                if times >= seconds_to_send_videos and recording:
                    recording = False
                    out.release()
                    await send_motion_video(session)

            cv2.imshow('Motion Detection', result_frame)

            if cv2.waitKey(30) & 0xFF == 27:
                break

        if out:
            out.release()

        cap.release()
        cv2.destroyAllWindows()

        await session.close()

if __name__ == "__main__":
    asyncio.run(main())

