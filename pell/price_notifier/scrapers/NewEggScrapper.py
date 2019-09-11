import re
import urllib.parse

import requests
from bs4 import BeautifulSoup as bSoup

from utils import utils


class NewEggScrapper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&DEPA=0&' \
               'Order=BESTMATCH&Description={}&N=-1&isNodeId=1'
    PRODUCT_FEATURES_CLASS_NAME = "description highlights text-left"
    PRODUCT_PRICE_CLASS_NAME = "price"
    PRODUCT_DESCRIPTION_CLASS_NAME = "description"
    PRODUCT_TITLE_CLASS_NAME = "col-lg-8 col-md-8 col-sm-8 col-xs-12 no-padding"
    PRODUCT_STOCK_CLASS_NAME = "product-stock"

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        encoded_url = NewEggScrapper.BASE_URL.format(urllib.parse.quote(product.name))
        data = bSoup(requests.get(encoded_url).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("div", {"class", "item-info"})

        # Get item information for each item in container
        if len(containers) > 0:
            for item in containers:
                # Only pick items with Free shipping and that are in stock
                is_in_stock = item is not None and \
                              item.find("p", {"class", "item-promo"}) and \
                              "out" not in item.find("p", {"class", "item-promo"}).text.lower()
                is_free_shipping = "free" in item.find("li", {"class", "price-ship"}).text.lower()
                if is_in_stock and is_free_shipping:
                    title = item.find("a", {"class", "item-title"}).text
                    brand = item.div.a.img["title"] if item.div.has_attr("a") else "-"
                    price = NewEggScrapper.extract_price(item)
                    link = item.find("a", {"class", "item-title"})["href"]

                    has_link = link is not None and not "-"
                    is_valid_price = price is not None and price > 0
                    if is_valid_price and has_link and int(price) <= int(product.baseline_price):
                        prompt = "\"" + title.replace(",", "|") + "\" is now available in: " + str(
                            price) + " at NewEgg (Baseline: " + product.baseline_price + ")"
                        details = utils.get_details(brand, price, title, link)
                        if utils.is_similar(title, product.description):
                            utils.print_similarity(title, product.description)
                            utils.display_windows_notification(brand, prompt)
                            utils.write_to_csv(details)

    @staticmethod
    def extract_price(item):
        price = re.sub(r'[\\|–-]', "", item.find("li", {"class", "price-current"}).text).strip()
        price = re.sub(r'[\xa0].*$', "", price).strip()
        price = price.replace("[$|,]", "")
        price = re.sub(r'[,$]', "", price).strip()
        price = float(price) * 100  # Convert USD to PKR since my list has prices in PKR
        return price
