import json
import math
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup as bSoup


class Product:
    def __init__(self, product):
        self.description = product["description"]
        self.name = product["name"]
        self.baseline_price = product["baseline_price"]
        # Allowed number representation in 'K' format (e.g. 3K, 10K etc) in json
        # Here while parsing, convert the prices with K notation to numeric value
        has_k_notation = str(self.baseline_price).lower().__contains__("k")
        price = self.baseline_price[:-1]
        self.baseline_price = str(int(price) * 1000) if has_k_notation else self.baseline_price


class CZoneScrapper:
    # Declare URL and class names to picked
    BASE_URL = 'http://www.czone.com.pk/search.aspx?kw={}'
    PRODUCT_FEATURES_CLASS_NAME = "description highlights text-left"
    PRODUCT_PRICE_CLASS_NAME = "price"
    PRODUCT_DESCRIPTION_CLASS_NAME = "description"
    PRODUCT_TITLE_CLASS_NAME = "col-lg-8 col-md-8 col-sm-8 col-xs-12 no-padding"
    PRODUCT_STOCK_CLASS_NAME = "product-stock"

    def search_item(self, product):
        # Read the page contents and get structured data using beautiful soup
        data = bSoup(requests.get(CZoneScrapper.BASE_URL.format(product.name)).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("div", {"class", "product"})

        # Get item information for each item in container
        if len(containers) > 0:
            for product in containers:
                # Only pick items that are available in stock
                stock_div = product.find("div", {"class", CZoneScrapper.PRODUCT_STOCK_CLASS_NAME})
                if "out" not in stock_div.findAll("span", {})[1].text.lower():
                    title_div = product.find(
                        "div", {"class", CZoneScrapper.PRODUCT_TITLE_CLASS_NAME}
                    )
                    desc_div = product.find(
                        "div", {"class", CZoneScrapper.PRODUCT_DESCRIPTION_CLASS_NAME}
                    )
                    price_div = product.find(
                        "div", {"class", CZoneScrapper.PRODUCT_PRICE_CLASS_NAME}
                    )
                    features_div = product.find(
                        "ul", {"class", CZoneScrapper.PRODUCT_FEATURES_CLASS_NAME}
                    )

                    title = title_div.h4.a.text
                    brand = product.find("span", {"class", "product-data"}).text
                    description = desc_div.findAll("p", {})[1].text
                    features = self.parse_features_list(features_div)
                    price = self.extract_price(price_div.span.text)

                    if int(price) <= int(product.baseline_price):
                        print("\"" + title.replace(",", "|") + "\" is now available at: " + str(price))
                        print("Product Details: ")
                        print(
                            title.replace(",", "|") + ", " +
                            brand.replace(",", "|") + ", " +
                            description.replace(",", "|") + ", " +
                            features.replace(",", "|") + ", " +
                            str(price) + "\n"
                        )

    @staticmethod
    def extract_price(price):
        if price is None:
            return 0
        price = str(price).lower().replace("rs.", "", 1)
        value = [int(s) for s in price.split() if s.isdigit()]
        price = price if len(value) == 0 else value[0]
        return price

    @staticmethod
    def parse_features_list(div):
        """
        Iterates over the supplied div element and creates pipe-separated string out of each item
        :return: pipe-separated string from <li/>
        """

        concat_features = ""
        for li in div.findAll("li", {}):
            concat_features = li.text + " | " + concat_features
        concat_features = concat_features[:-3] if concat_features.endswith(
            " | ") else concat_features
        return concat_features if len(concat_features) > 0 else "-"


class DarazScrapper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.daraz.pk/catalog/?q={}'

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        encoded_url = DarazScrapper.BASE_URL.format(urllib.parse.quote(product.name))
        data = bSoup(requests.get(encoded_url).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("script", {})[1]
        json_data = str(containers.text)
        json_data = json_data.split("\n")
        json_data = json_data[1]
        json_data = json_data.replace("jsTrackingStore.data = ", "")
        json_data = json_data.replace(";", "")
        json_data = json.loads(json_data)

        # Get item information for each item in container
        if len(json_data) > 0:
            for x in json_data["products"]:
                key = json_data["products"][x]
                title = key["name"]
                brand = key["brand"]
                description = "-"
                features = "-"
                price = key["priceLocal"]

                if math.floor(float(price)) <= int(product.baseline_price):
                    print("\"" + title.replace(",", "|") + "\" is now available at " + str(price) + " on Daraz")
                    print("Product Details: ")
                    print(
                        title.replace(",", "|") + ", " +
                        brand.replace(",", "|") + ", " +
                        description.replace(",", "|") + ", " +
                        features.replace(",", "|") + ", " +
                        str(price) + "\n"
                    )


class NewEggScrapper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description={}' \
               '&N=-1&isNodeId=1'
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
                is_in_stock = "out" not in item.find("p", {"class", "item-promo"}).text.lower()
                is_free_shipping = "free" in item.find("li", {"class", "price-ship"}).text.lower()
                if is_in_stock and is_free_shipping:
                    title = item.find("a", {"class", "item-title"}).text
                    description = "-"
                    features = "-"
                    brand = item.div.a.img["title"] if item.div.has_attr("a") else "-"
                    price = NewEggScrapper.extract_price(item)

                    if math.floor(price) <= int(product.baseline_price):
                        print("\"" + title.replace(",", "|") + "\" is now available at " + str(price) + " on NewEgg")
                        print("Product Details: ")
                        print(
                            title.replace(",", "|") + ", " +
                            brand.replace(",", "|") + ", " +
                            description.replace(",", "|") + ", " +
                            features.replace(",", "|") + ", " +
                            str(price) + "\n"
                        )

    @staticmethod
    def extract_price(item):
        price = re.sub(r'[–|-||]', "", item.find("li", {"class", "price-current"}).text).strip()
        price = re.sub(r'[\xa0].*$', "", price).strip()
        price = price.replace("$", "")
        price = float(price) * 100  # Convert USD to PKR since my list has prices in PKR
        return price


class AmazonScrapper:
    # Declare URL and class names to picked
    BASE_URL = 'https://www.amazon.com/s/ref=nb_sb_noss/134-4639554-0290304?url=search-alias%3Daps&field-keywords={}'
    PRODUCT_TITLE_CLASS_NAME = "a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal"
    PRODUCT_BRAND_CLASS_NAME = "a-size-small a-color-secondary"
    PRODUCT_PRICE_CLASS_NAME = "a-size-base a-color-base"
    PRODUCT_DESCRIPTION_CLASS_NAME = "a-size-small a-color-secondary"

    @staticmethod
    def search_item(product):
        # Read the page contents and get structured data using beautiful soup
        data = bSoup(requests.get(AmazonScrapper.BASE_URL.format(urllib.parse.quote(product.name))).text, "html.parser")

        # Find all the item containers
        containers = data.findAll("div", {"class", "a-fixed-left-grid-col a-col-right"})

        # Get item information for each item in container
        if len(containers) > 0:
            for item in containers:
                # Only pick items that are available in stock
                title_div = item.find(
                    "a", {"class", AmazonScrapper.PRODUCT_TITLE_CLASS_NAME}
                )
                price_div = item.find(
                    "span", {"class", AmazonScrapper.PRODUCT_PRICE_CLASS_NAME}
                )
                brand_div = item.findAll(
                    "span", {"class", AmazonScrapper.PRODUCT_BRAND_CLASS_NAME}
                )[1]

                title = title_div.text
                brand = brand_div.text
                description = "-"
                features = "-"
                price = AmazonScrapper.extract_price(price_div)

                if math.floor(price) <= int(product.baseline_price):
                    print("\"" + title.replace(",", "|") + "\" is now available at " + str(price) + " on Amazon")
                    print("Product Details: ")
                    print(
                        title.replace(",", "|") + ", " +
                        brand.replace(",", "|") + ", " +
                        description.replace(",", "|") + ", " +
                        features.replace(",", "|") + ", " +
                        str(price) + "\n"
                    )

    @staticmethod
    def extract_price(price_div):
        price = re.sub(r'[–|-||]', "", price_div.text).strip()
        price = re.sub(r'[\xa0].*$', "", price).strip()
        price = price.replace("$", "")
        price = float(price) * 100  # Convert USD to PKR since my list has prices in PKR
        return price


# Read all the items from the wishlist.json
with open('wishlist.json') as data_file:
    items = json.load(data_file)

# Parse JSON into an object with attributes corresponding to dict keys.
for i in items["items"]:
    p = Product(i)
    scrappers = [NewEggScrapper(), DarazScrapper(), CZoneScrapper(), AmazonScrapper()]
    for scrapper in scrappers:
       scrapper.search_item(p)
