import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class GoogleSearchAction:

    def __init__(self, command):
        self.command = command

    def execute(self):
        reg_ex = re.search('search for (.*)', self.command)
        search_for = self.command.split("search for", 1)[1]
        url = 'https://www.google.com/'
        if reg_ex:
            query = reg_ex.group(1)
            url = url + 'r/' + query
        # depends which web browser you are using
        driver = webdriver.Chrome(executable_path=r"chromedriver")
        driver.get('http://www.google.com')
        search = driver.find_element_by_name('q')
        search.send_keys(str(search_for))
        search.send_keys(Keys.RETURN)
        print('Opening URL: ', url)
        print('Done!')


if __name__ == "__main__":
    GoogleSearchAction("search for PELL").execute()
