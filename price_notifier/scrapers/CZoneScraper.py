import math

import requests
from bs4 import BeautifulSoup as bSoup

from utils import utils


class CZoneScraper:
    # Declare URL and class names to picked
    BASE_URL = 'http://www.czone.com.pk/search.aspx?kw={}'
    PRODUCT_PRICE_CLASS_NAME = "price"
    PRODUCT_TITLE_CLASS_NAME = "col-lg-8 col-md-8 col-sm-8 col-xs-12 no-padding"
    PRODUCT_STOCK_CLASS_NAME = "product-stock"
    PRODUCT_LINK_CLASS_NAME = "col-lg-8 col-md-8 col-sm-8 col-xs-12 no-padding"

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        data = bSoup(requests.get(CZoneScraper.BASE_URL.format(product.name)).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("div", {"class", "product"})

        # Get item information for each item in container
        if len(containers) > 0:
            for item in containers:
                # Only pick items that are available in stock
                stock_div = item.find("div", {"class", CZoneScraper.PRODUCT_STOCK_CLASS_NAME})
                if "out" not in stock_div.findAll("span", {})[1].text.lower():
                    title_div = item.find(
                        "div", {"class", CZoneScraper.PRODUCT_TITLE_CLASS_NAME}
                    )
                    price_div = item.find(
                        "div", {"class", CZoneScraper.PRODUCT_PRICE_CLASS_NAME}
                    )
                    link_div = item.find(
                        "div", {"class", CZoneScraper.PRODUCT_LINK_CLASS_NAME}
                    )

                    title = title_div.h4.a.text
                    link = "czone.com.pk" + link_div.h4.a["href"]
                    brand = item.find("span", {"class", "product-data"}).text
                    price = CZoneScraper.extract_price(price_div.span.text)

                    is_valid_price = price is not None and price > 0
                    if is_valid_price and int(price) <= int(product.baseline_price):
                        prompt = "\"" + title.replace(",", "|") + "\" is now available in: " + str(
                            price) + " at CZone (Baseline: " + product.baseline_price + ")"
                        details = utils.get_details(brand, price, title, link)
                        if utils.is_similar(title, product.description):
                            utils.print_similarity(title, product.description)
                            utils.display_windows_notification(brand, prompt)
                            utils.write_to_csv(details)

    @staticmethod
    def extract_price(price):
        if price is None:
            return 0
        price = str(price).lower().replace("rs.", "").replace(",", "")
        value = [int(s) for s in price.split() if s.isdigit()]
        price = price if len(value) == 0 else value[0]
        return math.floor(price)
