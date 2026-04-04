import os
import time
import threading
from subprocess import Popen
import RPi.GPIO as GPIO

# ---------- GPIO ----------
BUTTON_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---------- STATE ----------
mode = "video"
running_splash = False
busy = False

# ---------- PATHS ----------
SPLASH_DIR = "/home/pi/only-for-you/splash"
SOUND_FILE = "/home/pi/only-for-you/splash.mp3"


def get_images():
    return [
        os.path.join(SPLASH_DIR, f)
        for f in os.listdir(SPLASH_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]


def sound_loop():
    while running_splash:
        player = Popen(["mpg123", SOUND_FILE])
        player.wait()


def start_splash():
    global running_splash

    os.system("sudo systemctl stop love.service")
    os.system("sudo pkill -9 omxplayer.bin")

    images = get_images()

    if not images:
        return

    running_splash = True

    # slideshow без мигания консоли
    cmd = ["sudo", "fbi", "-T", "1", "-noverbose", "-a", "-t", "5"] + images
    Popen(cmd)

    threading.Thread(target=sound_loop, daemon=True).start()


def stop_splash():
    global running_splash

    running_splash = False

    os.system("sudo pkill fbi")
    os.system("sudo pkill mpg123")

    os.system("sudo dd if=/dev/zero of=/dev/fb0 bs=1M count=8 >/dev/null 2>&1")

    time.sleep(0.2)

    os.system("sudo systemctl start love.service")


def toggle_mode():
    global mode, busy

    if busy:
        return

    busy = True

    if mode == "video":
        start_splash()
        mode = "splash"
    else:
        stop_splash()
        mode = "video"

    time.sleep(0.3)

    busy = False


def button_callback(channel):
    threading.Thread(target=toggle_mode, daemon=True).start()


# ---------- BUTTON ----------
GPIO.add_event_detect(
    BUTTON_PIN,
    GPIO.BOTH,
    callback=button_callback,
    bouncetime=300
)

# ---------- LOOP ----------
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()

finally:
    GPIO.cleanup()
