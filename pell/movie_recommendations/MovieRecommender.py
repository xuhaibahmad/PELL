import http.client
import json
from collections import namedtuple

from movie_recommendations.config import Constants

conn = http.client.HTTPSConnection(Constants.API_ENDPOINT)
genre = []

# Fetch last used position
last_position = 0

# Read API Key from text file
try:
    with open(Constants.API_KEY_FILENAME) as api_key_file:
        api_key = api_key_file.read()
except FileNotFoundError:
    raise FileNotFoundError(Constants.ERROR_KEY_FILE_NOT_FOUND.format(Constants.API_KEY_FILENAME))

# Read genre prefs from JSON file
try:
    with open(Constants.SETTINGS_FILENAME) as settings_file:
        settings = json.load(settings_file)
        genre = settings["genre"]
except FileNotFoundError:
    raise FileNotFoundError(Constants.ERROR_KEY_FILE_NOT_FOUND.format(Constants.API_KEY_FILENAME))

# Fetch genre IDs
conn.request("GET", Constants.URL_GENRES.format(api_key))
response = conn.getresponse().read()
data = json.loads(response, object_hook=lambda d: namedtuple('genre', d.keys())(*d.values()))
genre_names = [g.name for g in data.genres if str(g.name) in genre]
genre_ids = [g.id for g in data.genres if str(g.name) in genre]
print("SELECTED GENRE NAME: {0}".format(genre_names))

# Fetch top 3 movies in defined categories
conn.request("GET", Constants.URL_MOVIES.format(api_key, genre_ids[0]))
response = conn.getresponse().read()
data = json.loads(response, object_hook=lambda d: namedtuple('movie', d.keys())(*d.values()))
recommendations = data.results[:3]
print("TOP 3 MOVIES IN SELECTED GENRES: {0}".format([r.title for r in recommendations]))

# Go to torrent website and search for these movies
# Download torrents to specified directory
# Notify when done
