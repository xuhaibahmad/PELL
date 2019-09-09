from .google_search_action import GoogleSearchAction


class Action:
    @staticmethod
    def from_command(self, command):
        if "search for" in command:
            return GoogleSearchAction(command)
