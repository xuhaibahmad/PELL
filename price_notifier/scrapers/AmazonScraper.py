import math
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup as bSoup

from utils import utils


class AmazonScraper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.amazon.com/s/ref=nb_sb_noss/134-4639554-0290304?' \
               'url=search-alias%3Daps&field-keywords={}'
    PRODUCT_TITLE_CLASS_NAME = "a-link-normal s-access-detail-page " \
                               "s-color-twister-title-link a-text-normal"
    PRODUCT_BRAND_CLASS_NAME = "a-size-small a-color-secondary"
    PRODUCT_PRICE_CLASS_NAME = "a-size-base a-color-base"

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        url = AmazonScraper.BASE_URL.format(urllib.parse.quote(product.name))
        data = bSoup(requests.get(url).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("div", {"class", "a-fixed-left-grid-col a-col-right"})

        # Get item information for each item in container
        if len(containers) > 0:
            for item in containers:
                # Only pick items that are available in stock
                title_div = item.find(
                    "a", {"class", AmazonScraper.PRODUCT_TITLE_CLASS_NAME}
                )
                price_div = item.find(
                    "span", {"class", AmazonScraper.PRODUCT_PRICE_CLASS_NAME}
                )
                brand_div = item.findAll(
                    "span", {"class", AmazonScraper.PRODUCT_BRAND_CLASS_NAME}
                )[1]

                title = title_div.text
                brand = brand_div.text
                price = AmazonScraper.extract_price(price_div)
                link = title_div["href"]

                has_link = link is not None and not "-"
                if float(product.baseline_price) >= math.floor(float(price)) > 0 and has_link:
                    prompt = "\"" + title.replace(",", "|") + "\" is now available in " + str(
                        price) + " at Amazon (Baseline: " + product.baseline_price + ")"
                    details = utils.get_details(brand, price, title, link)
                    if utils.is_similar(title, product.description):
                        utils.print_similarity(title, product.description)
                        utils.display_windows_notification(brand, prompt)
                        utils.write_to_csv(details)

    @staticmethod
    def extract_price(price_div):
        if price_div is None:
            return 0
        price = re.sub(r'[\\|–-]', "", price_div.text).strip()
        price = re.sub(r'[\xa0].*$', "", price).strip()
        price = re.sub(r'[$|,]', "", price).strip()
        price = float(price) * 100  # Convert USD to PKR since my list has prices in PKR
        return math.floor(price)
