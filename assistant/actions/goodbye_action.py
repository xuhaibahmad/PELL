import sys


class GoodbyeAction:

    def execute(self):
        sys.exit("Goodbye!")


if __name__ == "__main__":
    GoodbyeAction().execute()
