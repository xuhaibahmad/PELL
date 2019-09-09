from .google_search_action import GoogleSearchAction


def from_command(command):
    if "search for" in command:
        return GoogleSearchAction(command)
