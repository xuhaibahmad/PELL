import urllib.request
import urllib.parse
import re
import webbrowser
from pell.assistant.text_to_speech import talk
import time


class YoutubeAction:

    def __init__(self, command):
        self.command = command

    def execute(self):
        if "video of" in self.command:
            keyword = "video of"
        if "youtube" in self.command:
            keyword = "youtube"
        reg_ex = re.search('{} (.+)'.format(keyword), self.command)
        if reg_ex:
            domain = self.command.split(keyword, 1)[1]
            query_string = urllib.parse.urlencode({"search_query": domain})
            talk(
                "Here's what I could find about {0} on youtube".format(domain))
            time.sleep(2)
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string)
            # finds all links in search result
            search_results = re.findall(
                r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            webbrowser.open(
                "http://www.youtube.com/watch?v={}".format(search_results[0]))
            pass


if __name__ == "__main__":
    YoutubeAction("video of rick roll").execute()
