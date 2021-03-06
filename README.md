# PELL (Pet for Extremely Lazy Layman)

A hobby project for automation of everyday tasks.

## Purpose

The purpose of this project is to have very basic voice assistant that can automate various everyday tasks. Currently, following actions are supported:

- Email: Send emails using your Gmail account [commands: `send email` or `send mail`]
- Google Search: Let PELL Google That For You! [commands: `search for`]
- Wiki: Looks into wikipedia for given term and reads the first few paragraphs of the article to you [commands: `look for` or `what is` or `wikipedia`]
- Youtube: Opens Youtube video for given search phrase [commands: `video of` or `youtube`]
- Movie Recommendation: Loads 3 top rated movies in the given genre and attempts to open your selection in Netflix [commands: `recommend a movie` or `watch`]

## Usage

Launch the program using: `python3 -u "pell/assistant/assistant.py"` and give commands using your microphone. The system will be able to act as long as the spoken phrase contains one of the command keywords for the given action.

All actions can be found in `pell/actions/` directory. Each actions can be individually tested by running `python3 -u "pell/actions/<ACTION NAME>.py"`.

## Configurations

Some actions require API keys and user configurations for external resources. Create a `.env` file to provide sensitive information to the system.

The current version of PELL supports the following configurations:

```.env
# Email
test_email=[EMAIL ADDRESS TO SEND TEST EMAILS TO]
gmail_email=[YOUR GMAIL ID]
gmail_password=[YOUR GMAIL PASSWORD]

# Movies
tmdb_api_key=[Your TMDB API KEY]
netflix_email=[YOUR NETFLIX EMAIL]
netflix_password=[YOUR NETFLIX PASSWORD]
netflix_profile=[NETFLIX PROFILE TO USE]

# Books
books_dir=[BOOKS DIRECTORY ON YOUR FILESYSTEM]
```
