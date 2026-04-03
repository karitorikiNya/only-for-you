import os
import time
import random
from subprocess import Popen
import RPi.GPIO as GPIO

# ---------- GPIO ----------
BUTTON_PIN = 6 #26

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

os.system('raspi-gpio set 19 op a5')
GPIO.output(18, GPIO.HIGH)

# ---------- STATE ----------
skip = False
player = None

def button_callback(channel):
    global skip
    skip = True
    os.system("pkill -9 omxplayer.bin")

GPIO.add_event_detect(
    BUTTON_PIN,
    GPIO.FALLING,
    callback=button_callback,
    bouncetime=300
)

# ---------- VIDEOS ----------
directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'videos')
videos = []
index = 0

def loadVideos():
    """Загрузить все mp4 и перемешать их"""
    global videos, index
    videos = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith('.mp4')
    ]
    random.shuffle(videos)
    index = 0

def playLoop():
    """Бесконечный цикл воспроизведения видео"""
    global index, skip

    while True:
        if not videos or index >= len(videos):
            loadVideos()  # начинаем новый цикл с рандомной последовательностью

        skip = False
        current_video = videos[index]

        player = Popen([
            'omxplayer',
            '--no-osd', '--blank',
            '--aspect-mode', 'fill',
            current_video
        ])

        player.wait()  # ждем конца видео ИЛИ кнопки

        # После окончания/пропуска идем к следующему
        index += 1
        time.sleep(0.1)  # антидребезг и плавный переход

# ---------- MAIN ----------
try:
    loadVideos()  # первый раз
    playLoop()    # старт цикла
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
