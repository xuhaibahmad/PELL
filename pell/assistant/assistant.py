from gtts import gTTS
import speech_recognition as sr
from pygame import mixer
from text_to_speech import talk, listen
from pell.actions import action


def listen_for_commands():
    command = listen()
    print('You said: ' + command + '\n')
    action.from_command(command).execute()
    return command


talk('PELL is ready!')

while True:
    listen_for_commands()
