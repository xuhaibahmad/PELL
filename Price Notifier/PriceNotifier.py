import json
import math
import re
import time
import urllib.parse
from time import strftime, gmtime
import requests
from bs4 import BeautifulSoup as bSoup
from win10toast import ToastNotifier
from difflib import SequenceMatcher

NOTIFICATION_ICON_PATH = "D:\Zuhaib\Misc\Python Workspace\PELL\icons.ico"


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
                        details = get_details(brand, price, title, link)
                        if is_similar(title, product.description):
                            print_similarity(title, product.description)
                            display_windows_notification(brand, prompt)
                            write_to_csv(details)

    @staticmethod
    def extract_price(price):
        if price is None:
            return 0
        price = str(price).lower().replace("rs.", "").replace(",", "")
        value = [int(s) for s in price.split() if s.isdigit()]
        price = price if len(value) == 0 else value[0]
        return math.floor(price)


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
                    details = get_details(brand, price, title, link)
                    if is_similar(title, product.description):
                        print_similarity(title, product.description)
                        display_windows_notification(brand, prompt)
                        write_to_csv(details)


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

                if float(product.baseline_price) >= math.floor(float(price)) > 0:
                    prompt = "\"" + title.replace(",", "|") + "\" is now available in " + str(
                        price) + " at Amazon (Baseline: " + product.baseline_price + ")"
                    details = get_details(brand, price, title, link)
                    if is_similar(title, product.description):
                        print_similarity(title, product.description)
                        display_windows_notification(brand, prompt)
                        write_to_csv(details)

    @staticmethod
    def extract_price(price_div):
        if price_div is None:
            return 0
        price = re.sub(r'[–|-||]', "", price_div.text).strip()
        price = re.sub(r'[\xa0].*$', "", price).strip()
        price = price.replace("$", "")
        price = float(price) * 100  # Convert USD to PKR since my list has prices in PKR
        return math.floor(price)


def get_details(brand, price, title, link):
    details = title.replace(",", "|") + ", " + \
              brand.replace(",", "|") + ", " + \
              str(math.floor(float(price))) + ", " + \
              link
    return details


def write_to_csv(details):
    file = open("available_wishlist_products.csv", "a")
    time = strftime("%a, %d %b %Y", gmtime())
    details = time.replace(",", " ") + ", " + details + "\n"
    file.write(details)
    file.close()
    print("\nProduct Details: ")
    print(details)


def is_similar(a, b):
    similarity_percent = SequenceMatcher(None, a, b).ratio() * 100
    return similarity_percent > 45


def print_similarity(a, b):
    similarity_percent = SequenceMatcher(None, a, b).ratio() * 100
    print("Similarity % between " + b + " and " + a + ": " + str(similarity_percent))


def display_windows_notification(title, msg):
    print(msg)
    notification = ToastNotifier()
    notification.show_toast(title, msg, icon_path=NOTIFICATION_ICON_PATH, duration=30)


# Read all the items from the wishlist.json
with open('wishlist.json') as data_file:
    items = json.load(data_file)

# Create csv file to write available items to
filename = "available_wishlist_products.csv"
f = open(filename, "w")
headers = "Date, Title, Brand, Price, Link\n"
f.write(headers)
f.close()

# Parse JSON into an object with attributes corresponding to dict keys.
scrapers = [DarazScraper(), CZoneScraper(), AmazonScraper(), NewEggScrapper()]
for i in items["items"]:
    p = Product(i)
    for scraper in scrapers:
        scraper.search_item(p)
        time.sleep(5)
