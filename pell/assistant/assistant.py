from gtts import gTTS
import speech_recognition as sr
from pygame import mixer
from text_to_speech import talk, listen
from pell.actions import action


def listen_for_commands():
    # Initialize the recognizer
    r = sr.Recognizer()
    audio = listen()
    try:
        command = r.recognize_google(audio).lower()
        print('You said: ' + command + '\n')
        action.from_command(command).execute()

    # loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        print('Your last command couldn\'t be heard')
        command = listen_for_commands()

    return command


talk('PELL is ready!')

while True:
    listen_for_commands()
