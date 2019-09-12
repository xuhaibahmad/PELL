from pell.actions.google_search_action import GoogleSearchAction
from pell.actions.goodbye_action import GoodbyeAction
from pell.actions.greeting_action import GreetingAction
from pell.actions.email_action import EmailAction
from pell.actions.wiki_action import WikiAction
from pell.actions.stop_talking_action import StopTalkingAction


def from_command(command):
    if "search for" in command:
        return GoogleSearchAction(command)
    elif "goodbye pell" in command:
        return GoodbyeAction()
    elif "send email" or "send mail" in command:
        return EmailAction(command)
    elif "look for" or "what is" or "wikipedia" in command:
        return WikiAction(command)
    elif "stop talking" or "thanks" or "alright" in command:
        return StopTalkingAction()
    else:
        return GreetingAction(command)
