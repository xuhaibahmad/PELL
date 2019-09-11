from pell.assistant.text_to_speech import talk, listen
import random
import sys


class GreetingAction:

    def __init__(self, command):
        self.command = command

    def execute(self):
        errors = [
            "I don\'t know what you mean!",
            "Excuse me?",
            "Can you repeat it please?",
        ]

        if 'hello' in self.command:
            talk('Hello! I am PELL. How can I help you?')
        else:
            error = random.choice(errors)
            talk(error)


if __name__ == "__main__":
    while True:
        GreetingAction("hello").execute()
        listen()
        sys.exit()
