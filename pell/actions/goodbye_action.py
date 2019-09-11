import sys
from pell.assistant.text_to_speech import talk, listen
import sys


class GoodbyeAction:

    def execute(self):
        talk("Goodbye!")
        # TODO Wait few seconds before closing
        if __name__ != "__main__":
            sys.exit("Goodbye!")


if __name__ == "__main__":
    while True:
        GoodbyeAction().execute()
        listen()
        sys.exit()
