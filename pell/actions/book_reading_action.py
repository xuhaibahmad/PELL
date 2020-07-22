from pell.assistant.text_to_speech import talk, listen
import json
import sys

class ReadBookAction:
    def __init__(self, command, book=None):
        self.command = command
        self.book = book
        with open('config.json') as f:
            data = json.load(f)
            self.books_dir = data["books_dir"]
        
    def execute(self):
        if self.book == None:
            talk('Which book do you want to listen?')
            time.sleep(3)
            self.book = listen()
        # Check if book exists
        print("Looking for {} in {}".format(self.book, self.books_dir))

if __name__ == "__main__":
    ReadBookAction(
        "Read a book",
        "Alchemist",
    ).execute()
