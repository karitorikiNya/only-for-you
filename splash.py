import os
import time
import threading
import random
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
MUSIC_DIR = "/home/pi/only-for-you/music"

# ---------- IMAGES ----------
def get_images():
    images = [
        os.path.join(SPLASH_DIR, f)
        for f in os.listdir(SPLASH_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    random.shuffle(images)
    return images

# ---------- MUSIC ----------
def get_sounds():
    sounds = [
        os.path.join(MUSIC_DIR, f)
        for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith((".mp3", ".wav"))
    ]
    random.shuffle(sounds)
    return sounds

def get_audio_duration(sound):
    import subprocess
    try:
        result = subprocess.check_output([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            sound
        ])
        return float(result.decode().strip())
    except:
        return 0

def sound_loop():
    global running_splash
    while running_splash:
        playlist = get_sounds()
        if not playlist:
            time.sleep(1)
            continue

        for sound in playlist:
            if not running_splash:
                break

            duration = get_audio_duration(sound)
            if duration <= 4:
                fade_out_start = max(duration - 1, 0)
                fade_duration = 1
            else:
                fade_out_start = duration - 2
                fade_duration = 2

            player = Popen([
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-volume", "25",
                "-af",
                f"afade=t=in:ss=0:d=2,afade=t=out:st={fade_out_start}:d={fade_duration}",
                sound
            ], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            player.wait()

# ---------- SPLASH ----------
def start_splash():
    global running_splash
    os.system("sudo systemctl stop VictoriasSecret.service")
    os.system("sudo pkill -9 omxplayer.bin")

    images = get_images()
    if not images:
        return

    running_splash = True

    cmd = ["sudo", "fbi", "-T", "7", "-noverbose", "-a", "-t", "5"] + images
    Popen(cmd, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))

    # Плейлист музыки
    threading.Thread(target=sound_loop, daemon=True).start()

def stop_splash():
    global running_splash
    running_splash = False

    os.system("sudo pkill fbi")
    os.system("sudo pkill ffplay")

    os.system("sudo dd if=/dev/zero of=/dev/fb0 bs=1M count=8 >/dev/null 2>&1")
    time.sleep(0.2)
    os.system("sudo systemctl start VictoriasSecret.service")

# ---------- TOGGLE ----------
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

GPIO.add_event_detect(
    BUTTON_PIN,
    GPIO.BOTH,
    callback=button_callback,
    bouncetime=300
)

# ---------- MAIN LOOP ----------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
