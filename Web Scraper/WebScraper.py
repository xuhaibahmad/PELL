from urllib.request import urlopen as request
import re
from bs4 import BeautifulSoup as bSoup
from time import gmtime, strftime

# Declare the url to be scrapped
url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20cards'

# Open network connection and read the page contents
client = request(url)
pageHtml = client.read()
client.close()

# Get structured data using beautiful soup
data = bSoup(pageHtml, "html.parser")

# Find all the item containers
containers = data.findAll("div", {"class", "item-info"})

# Write contents to a csv file
if len(containers) > 0:
    filename = "scrapped_products.csv"
    f = open(filename, "w")
    headers = "Title, Brand, Price\n"
    f.write(headers)

    # Get item information for each item in container
    for item in containers:
        # Only pick items with Free shipping
        if "free" in item.find("li", {"class", "price-ship"}).text.lower():
            title = item.find("a", {"class", "item-title"}).text
            brand = item.div.a.img["title"] if item.div.has_attr("a") else "-"
            price = re.sub(r'[–|-||]', "", item.find("li", {"class", "price-current"}).text).strip()
            f.write(title.replace(",", "|") + ", " + brand.replace(",", "|") + ", " + price + "\n")

    f.close()
    print("Items updated at " + strftime("%a, %d %b %Y %X +0000", gmtime()))
