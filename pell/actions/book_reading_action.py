
from collections import OrderedDict
from pell.assistant.text_to_speech import talk, listen, read
import json
import os
import functools
import operator
import slate3k
import re

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
        print("Looking for {} in {}...".format(self.book, self.books_dir))
        books = find_all(self.book, self.books_dir)
        if len(books) > 0:
            read_file(self, books[0])
        else:
            talk("Sorry, could not find a book with this title")

def read_file(self, file):
    # Convert PDF to Text
    with open("{}".format(file), "rb") as f:
        pdf = slate3k.PDF(f)
    # Write converted text to a Text file
    with open("{}.txt".format(self.book), "w") as f:
        for page in pdf:
            # TODO: The text needs to be more refined to avoid unnecessary line breaks
            text = re.sub(r'(?<=[a-z., ]{2})\n(?!\n)', '', page)
            f.write(text)
    # Read the text file page by page
    with open("{}.txt".format(self.book), "rb") as f:
        print("Now Reading: {}".format(self.book))
        for index, page in enumerate(pdf):
            if bool(page and page.strip()):
                print("Reading Page: {}".format(index))
                read(page, prompt=False)    


def find_all(name, path):
    result = []
    for _, _, files in os.walk(path):
        result.append([os.path.join(path, f) for f in files if name in f])
    return functools.reduce(operator.iconcat, result, [])

if __name__ == "__main__":
    ReadBookAction(
        "Read a book",
        "Alchemist",
    ).execute()
