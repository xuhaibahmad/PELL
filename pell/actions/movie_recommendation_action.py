from pell.assistant.text_to_speech import talk, listen
import json
from const import API_ENDPOINT, URL_GENRES, URL_MOVIES, ROOT_DIR
import http.client
from collections import namedtuple
import os
import re
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import webbrowser
import time
from difflib import SequenceMatcher
import sys


class MovieRecommendationAction:

    def __init__(self, command, genre=None):
        self.command = command
        self.genre = genre
        self.conn = http.client.HTTPSConnection(API_ENDPOINT)
        with open('config.json') as f:
            data = json.load(f)
            movie_config = data["movie"]
            self.email = movie_config["email"]
            self.password = movie_config["password"]
            self.profile = movie_config["profile"]
            api_key_file = movie_config["api_key_filename"]
            self.api_key = self.read_api_key(api_key_file)

    def read_api_key(self, filename):
        path = os.path.join(ROOT_DIR, filename)
        with open(path) as api_key_file:
            return api_key_file.read()

    def execute(self):
        # Ask for genre only if not provided
        if self.genre is None:
            talk("Alright! Which genre?")
            self.genre = listen()

        movies = self.get_movies(self.genre)
        selection = self.get_movie_selection(movies)

        if selection is None:
            talk("Ah.. That's all I have. Sorry I couldn't help you!")
        else:
            talk("Alright, we are going to watch {}. Opening on netflix now.".format(
                selection.title))
            link = self.get_netflix_link(
                selection.title, self.email, self.password, self.profile)
            if link is None:
                talk(
                    "Uh-oh! Looks like this item is not available on netflix. Do you want to retry?")
                retry = listen()
                if "yes" in retry:
                    MovieRecommendationAction(self.command).execute()
                else:
                    talk("Alright!")
            else:
                webbrowser.open(link)

    def get_movie_selection(self, movies):
        selection = None
        for movie in movies:
            movie_name = movie.title
            talk("Have you watched {}".format(movie_name))
            answer = listen()
            if answer is None:
                selection = movie
                break
            elif "no" in answer:
                selection = movie
                break
            else:
                continue
        return selection

    def get_movies(self, genre):
        # Fetch genre IDs
        self.conn.request("GET", URL_GENRES.format(self.api_key))
        response = self.conn.getresponse().read()
        data = json.loads(
            response,
            object_hook=lambda d: namedtuple('genre', d.keys())(*d.values())
        )
        genre_names = [g.name for g in data.genres if str(g.name) in genre]
        genre_ids = [g.id for g in data.genres if str(g.name) in genre]
        print("SELECTED GENRE: {0}".format(genre_names))
        if not genre_names:
            self.handle_genre_error()
        else:
            # Fetch top 3 movies in defined categories
            self.conn.request(
                "GET",
                URL_MOVIES.format(self.api_key, genre_ids[0])
            )
            response = self.conn.getresponse().read()
            data = json.loads(
                response,
                object_hook=lambda d: namedtuple(
                    'movie', d.keys())(*d.values())
            )
            recommendations = data.results[:3]
            print("TOP 3 MOVIES IN SELECTED GENRES: {0}".format(
                [r.title for r in recommendations]))
            return recommendations

    def handle_genre_error(self):
        talk(
            "I don't have any information about this genre, whould you like to try another?")
        genre_retry = listen()
        if "yes" in genre_retry:
            talk("Okay, which genre?")
            g = listen()
            self.get_movies(g)
        else:
            talk("Alright!")
            sys.exit()

    def get_netflix_link(self, name, email, password, profile):
        print("Searching for ", name)
        driver = webdriver.Chrome(executable_path=r"chromedriver")
        driver.get("https://www.netflix.com/browse")

        # Login
        email_field = driver.find_element_by_name('userLoginId')
        password_field = driver.find_element_by_name('password')
        email_field.send_keys(str(email))
        password_field.send_keys(str(password))
        password_field.send_keys(Keys.RETURN)

        # Open profile
        item = [
            p
            for p in driver.find_elements_by_class_name("profile-name")
            if profile in p.get_attribute("innerHTML")
        ][0]
        item.click()

        # Search
        driver.find_element_by_class_name("icon-search").click()
        search_field = driver.find_element_by_xpath(
            "//input[@data-uia='search-box-input']")
        search_field.send_keys(str(name))
        search_field.send_keys(Keys.RETURN)

        # Extract most identical item in the list
        time.sleep(3)
        movies = [
            m.get_attribute("href")
            for m in driver.find_elements_by_xpath('//a[contains(@href, "%s")]' % "watch")
            if self.is_similar(name, m.text)
        ]

        try:
            movie = movies[0]
        except IndexError:
            movie = None

        driver.quit()
        return movie

    def is_similar(self, a, b):
        percent = SequenceMatcher(None, a, b).ratio() * 100
        print("Similarity b/e {0} & {1} = {2}".format(a, b, percent))
        return percent > 75


if __name__ == "__main__":
    '''
    TODO This action can be vastly improved with the help of term extraction
    currently we are not processing the possibility of user providing information
    about the criteria e.g. Genre, Release Year, Actors, Rating etc.
    '''
    MovieRecommendationAction(
        "Recommend a good movie",
        "Science Fiction"
    ).execute()
