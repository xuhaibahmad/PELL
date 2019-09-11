from .google_search_action import GoogleSearchAction
from .goodbye_action import GoodbyeAction


def from_command(command):
    if "search for" in command:
        return GoogleSearchAction(command)
    elif "goodbye pell" in command:
        return GoodbyeAction()
