import math
from difflib import SequenceMatcher
from time import strftime, gmtime

from win10toast import ToastNotifier

from price_notifier import config


def get_details(brand, price, title, link):
    details = title.replace(",", "|") + ", " + \
              brand.replace(",", "|") + ", " + \
              str(math.floor(float(price))) + ", " + \
              link
    return details


def write_to_csv(details):
    file = open(config.Constants.OUTPUT_FILENAME, "a")
    details = strftime("%a, %d %b %Y", gmtime()).replace(",", " ") + ", " + details + "\n"
    file.write(details)
    file.close()
    print("\nProduct Details: ")
    print(details)


def is_similar(a, b):
    similarity_percent = SequenceMatcher(None, a, b).ratio() * 100
    return similarity_percent > config.Constants.SIMILARITY_PERCENT


def print_similarity(a, b):
    similarity_percent = SequenceMatcher(None, a, b).ratio() * 100
    print("Similarity % between " + b + " and " + a + ": " + str(similarity_percent))


def display_windows_notification(title, message):
    print(message)
    notification = ToastNotifier()
    notification.show_toast(title, message,
                            icon_path=config.Constants.NOTIFICATION_ICON_PATH,
                            duration=config.Constants.NOTIFICATION_DURATION)
