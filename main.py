import cv2
import telebot
import time

# Замените на ваш токен бота
TOKEN = '6350121672:AAEsGxrOAtBpci8MXpp9nRpZUnVQjQCQyCg'

# Замените на ваш чат ID (можно узнать у бота @userinfobot в Телеграме)
CHAT_ID = '888797603'

bot = telebot.TeleBot(TOKEN)

def motion_detection(frame, motion_detector, threshold_area):
    fg_mask = motion_detector.apply(frame)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threshold_area:
            return True

    return False

def main():
    cap = cv2.VideoCapture(0)
    motion_detector = cv2.createBackgroundSubtractorMOG2()
    threshold_area = 1000
    interval = 10  # Интервал отправки сообщений (в секундах)
    last_send_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if motion_detection(frame, motion_detector, threshold_area):
            current_time = time.time()
            if current_time - last_send_time >= interval:
                last_send_time = current_time

                cv2.imwrite('motion_detected.jpg', frame)
                with open('motion_detected.jpg', 'rb') as photo:
                    bot.send_photo(CHAT_ID, photo)

        cv2.imshow('Motion Detection', frame)

        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
