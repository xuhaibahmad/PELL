from pell.assistant.text_to_speech import talk, listen, read
import bs4
import requests
import re
import time


class WikiAction:

    def __init__(self, command):
        self.command = command

    def execute(self):
        reg_ex = re.search('search in wikipedia (.+)', self.command)
        if reg_ex:
            query = self.command.split()
            keyword = query[3]

            response = requests.get("https://en.wikipedia.org/wiki/" + keyword)

            if response is not None:
                html = bs4.BeautifulSoup(response.text, 'html.parser')
                title = html.select("#firstHeading")[0].text
                talk(
                    "Here's what I could find about {0} on the internet. According to wikipedia".format(title))
                time.sleep(2)
                paragraphs = html.select("p")
                for para in paragraphs:
                    print(para.text)

                intro = '\n'.join([para.text for para in paragraphs[0:3]])
                read(intro)


if __name__ == "__main__":
    WikiAction("search in wikipedia mars").execute()
