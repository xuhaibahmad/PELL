from pell.actions.google_search_action import GoogleSearchAction
from pell.actions.goodbye_action import GoodbyeAction
from pell.actions.greeting_action import GreetingAction
from pell.actions.email_action import EmailAction


def from_command(command):
    if "search for" in command:
        return GoogleSearchAction(command)
    elif "goodbye pell" in command:
        return GoodbyeAction()
    elif "send email" or "send mail" in command:
        return EmailAction(command)
    else:
        return GreetingAction(command)
