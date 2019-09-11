from pell.actions.google_search_action import GoogleSearchAction
from pell.actions.goodbye_action import GoodbyeAction
from pell.actions.greeting_action import GreetingAction


def from_command(command):
    if "search for" in command:
        return GoogleSearchAction(command)
    elif "goodbye pell" in command:
        return GoodbyeAction()
    else:
        return GreetingAction(command)
