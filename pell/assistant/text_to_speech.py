from gtts import gTTS
import speech_recognition as sr
from pygame import mixer
import os
from const import ROOT_DIR
import time
import readtime

AUDIO_PATH = os.path.join(ROOT_DIR, 'bin/audio.mp3')
SPEECH_PATH = os.path.join(ROOT_DIR, 'bin/speech.mp3')


def talk(audio):
    print(audio)
    for line in audio.splitlines():
        text_to_speech = gTTS(text=audio, lang='en-us')
        text_to_speech.save(AUDIO_PATH)
        mixer.init()
        mixer.music.load(AUDIO_PATH)
        mixer.music.play()
        time.sleep(3)


def read(audio):
    print(audio)
    text_to_speech = gTTS(text=audio, lang='en-us')
    text_to_speech.save(SPEECH_PATH)
    mixer.init()
    mixer.music.load(SPEECH_PATH)
    mixer.music.play()
    wait_time = readtime.of_text(audio)
    time.sleep(wait_time.seconds*2)


def listen():
    # Initialize the recognizer
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('PELL is Ready...')
        r.pause_threshold = 1
        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source, duration=1)
        # listens for the user's input
        audio = r.listen(source)
        return audio


def stop_talking():
    mixer.music.stop()
