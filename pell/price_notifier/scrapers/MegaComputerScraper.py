import math
import urllib.parse

import requests
from bs4 import BeautifulSoup as bSoup

from utils import utils


class MegaComputerScraper:
    # Declare URL and class names to picked
    BASE_URL = 'http://www.megacomputer.pk/catalogsearch/result/index/?is_ajax=1&limit=36&q={}'
    PRODUCT_PRICE_CLASS_NAME = "old-price"
    PRODUCT_PRICE_CLASS_NAME_SECONDARY = "price-box"
    PRODUCT_SPECIAL_PRICE_CLASS_NAME = "special-price"
    PRODUCT_TITLE_CLASS_NAME = "product-name"

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        url = MegaComputerScraper.BASE_URL.format(urllib.parse.quote(product.name))
        data = bSoup(requests.get(url).text, "html.parser")

        # Find main container
        main = data.find("div", {"class", "main"})

        # Find all the item containers
        containers = main.findAll("li", {"class", "item"})

        # Get item information for each item in container
        if len(containers) > 0:
            for item in containers:
                title_div = item.find(
                    "h2", {"class", MegaComputerScraper.PRODUCT_TITLE_CLASS_NAME}
                )
                price_div = item.find(
                    "p", {"class", MegaComputerScraper.PRODUCT_PRICE_CLASS_NAME}
                )
                special_price_div = item.find(
                    "p", {"class", MegaComputerScraper.PRODUCT_SPECIAL_PRICE_CLASS_NAME}
                )
                secondary_price_div = item.find(
                    "div", {"class", MegaComputerScraper.PRODUCT_PRICE_CLASS_NAME_SECONDARY}
                )

                has_price_div = price_div is not None
                has_special_price_div = special_price_div is not None
                has_secondary_price_div = secondary_price_div is not None

                price_div = price_div.findAll("span", {})[1] \
                    if has_price_div else None
                special_price_div = special_price_div.findAll("span", {})[1] \
                    if has_special_price_div else None
                secondary_price_div = secondary_price_div.findAll("span", {})[1] \
                    if has_secondary_price_div else None

                title = title_div.a["title"]
                brand = str(title).split(" ", 1)
                brand = brand[0] if len(brand) > 0 else "-"
                link = title_div.a["href"]

                if has_special_price_div:
                    price = special_price_div.text
                elif has_price_div:
                    price = price_div.text
                elif has_secondary_price_div:
                    price = secondary_price_div.text
                else:
                    price = 0

                price = MegaComputerScraper.extract_price(price)

                is_valid_price = price is not None and price > 0
                if is_valid_price and int(price) <= int(product.baseline_price):
                    prompt = "\"" + title.replace(",", "|") + "\" is now available in: " + str(
                        price) + " at Mega Computer (Baseline: " + product.baseline_price + ")"
                    details = utils.get_details(brand, price, title, link)
                    if utils.is_similar(title, product.description):
                        utils.print_similarity(title, product.description)
                        utils.display_windows_notification(brand, prompt)
                        utils.write_to_csv(details)

    @staticmethod
    def extract_price(price):
        if price is None:
            return 0
        price = str(price).lower().replace(" ", "").replace("pkr", "").replace(",", "")
        value = [int(s) for s in price.split() if s.isdigit()]
        price = price if len(value) == 0 else value[0]
        return math.floor(float(price))
