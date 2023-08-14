
# Замените на ваш токен бота
TOKEN = '6350121672:AAEsGxrOAtBpci8MXpp9nRpZUnVQjQCQyCg'

# Замените на ваш чат ID (можно узнать у бота @userinfobot в Телеграме)
CHAT_ID = '888797603'

import cv2
import asyncio
from aiogram import Bot, types
from aiogram.utils import executor
import time
from moviepy.editor import VideoFileClip



bot = Bot(token=TOKEN)
loop = asyncio.get_event_loop()

frame_count = 0

def motion_detection(frame, motion_detector, threshold_area):
    global frame_count
    fg_mask = motion_detector.apply(frame)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threshold_area:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Рисуем рамку вокруг объекта
            motion_detected = True

    return frame, motion_detected

async def send_motion_photo():
    with open('motion_photo.jpg', 'rb') as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=types.InputFile(photo))

async def send_motion_video():
    from moviepy.editor import VideoFileClip
    import os

    # Конвертировать AVI видео в MP4
    clip = VideoFileClip('motion_detected.avi')
    clip.write_videofile('motion_detected.mp4', codec='libx264', threads=4)

    # Отправить видео в Телеграм
    with open('motion_detected.mp4', 'rb') as video:
        await bot.send_video(chat_id=CHAT_ID, video=types.InputFile(video))

    # Удалить AVI файл после конвертации
    os.remove('motion_detected.avi')

async def main():
    global frame_count
    cap = cv2.VideoCapture(1)
    motion_detector = cv2.createBackgroundSubtractorMOG2()
    threshold_area = 3000

    recording = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None

    last_photo_time = 0
    last_send_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        result_frame, motion_detected = motion_detection(frame, motion_detector, threshold_area)

        if motion_detected:
            frame_count += 1
            if frame_count >= 5:  # Отправить кадр после пяти кадров
                frame_count = 0
                if not recording:
                    recording = True
                    out = cv2.VideoWriter('motion_detected.avi', fourcc, 20.0, (640, 480))
                    last_send_time = current_time

                out.write(frame)

                if current_time - last_photo_time >= 20:
                    last_photo_time = current_time
                    cv2.imwrite('motion_photo.jpg', result_frame)
                    await send_motion_photo()

        else:
            frame_count = 0  # Сбрасываем счетчик кадров при прекращении движения
            if recording:
                recording = False
                out.release()

                if current_time - last_send_time >= 30:
                    await send_motion_video()
                    last_send_time = current_time

        cv2.imshow('Motion Detection', result_frame)

        if cv2.waitKey(30) & 0xFF == 27:
            break

    if out:
        out.release()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    loop.run_until_complete(main())
