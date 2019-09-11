import json
import time
import traceback

from Product import Product

from price_notifier.config import Constants

# Read all the items from the wish list json file
with open(Constants.WISHLIST_FILENAME) as data_file:
    items = json.load(data_file)

# Create csv file to write available items to
filename = "%s" % Constants.OUTPUT_FILENAME
f = open(filename, "w")
headers = "Date, Title, Brand, Price, Link\n"
f.write(headers)
f.close()

# Declare the list of parsers you want to use in Config.py file inside Constants class
# Organizing this way so everyone can have their own set of File names, Notification icons,
# durations and set of parsers without modifying the main codebase
scrapers = Constants.MY_SCRAPERS

# Parse JSON for each item into a Product object and pass it to scraper for further processing.
for i in items["items"]:
    p = Product(i)
    for scraper in scrapers:
        if p is not None:
            try:
                scraper.search_item(p)
            except Exception as err:
                print("Exception in item " + p.description + " in " + str(
                    scraper.__class__) + " scraper")
                traceback.print_tb(err.__traceback__)
                continue
            time.sleep(5)
