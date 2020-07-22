import os
from dotenv import load_dotenv
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

API_ENDPOINT = "api.themoviedb.org"
URL_GENRES = "/3/genre/movie/list?language=en-US&api_key={0}"
URL_MOVIES = "/3/discover/movie?api_key={0}&language=en-US" \
    "&sort_by=popularity.desc&include_adult=true&include_video=false&page=1" \
    "&with_genres={1}"
