import json
import math
import urllib.parse

import requests
from bs4 import BeautifulSoup as bSoup

from utils import utils


class DarazScraper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.daraz.pk/catalog/?q={}'

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        encoded_url = DarazScraper.BASE_URL.format(urllib.parse.quote(product.name))
        data = bSoup(requests.get(encoded_url).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("script", {})[1]

        # Extract JSON from extracted script
        json_data = str(containers.text)
        json_data = json_data.split("\n")

        if json_data is None or len(json_data) < 2:
            print("Invalid JSON in Daraz sraper: " + str(json))
            return

        json_data = json_data[1]
        json_data = json_data.replace("jsTrackingStore.data = ", "")
        json_data = json_data.replace(";", "")
        json_data = json.loads(json_data)

        # Get item information for each item in json
        if len(json_data) > 0:
            for x in json_data["products"]:
                link = "-"
                for div in data.findAll("div", {"class", "sku -gallery"}):
                    if div["data-sku"] == x:
                        link = div.a["href"]

                key = json_data["products"][x]
                title = key["name"]
                brand = key["brand"]
                price = key["priceLocal"]

                if float(product.baseline_price) >= math.floor(float(price)) > 0:
                    prompt = "\"" + title.replace(",", "|") + "\" is now available in " + str(
                        price) + " at Daraz (Baseline: " + product.baseline_price + ")"
                    details = utils.get_details(brand, price, title, link)
                    if utils.is_similar(title, product.description):
                        utils.print_similarity(title, product.description)
                        utils.display_windows_notification(brand, prompt)
                        utils.write_to_csv(details)
