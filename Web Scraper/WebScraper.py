import requests
from bs4 import BeautifulSoup as bSoup
from time import gmtime, strftime

# Declare URL and class names to picked
URL = 'http://www.czone.com.pk/graphic-cards-pakistan-ppt.154.aspx'
PRODUCT_FEATURES_CLASS_NAME = "description highlights text-left"
PRODUCT_PRICE_CLASS_NAME = "price"
PRODUCT_DESCRIPTION_CLASS_NAME = "description"
PRODUCT_TITLE_CLASS_NAME = "col-lg-8 col-md-8 col-sm-8 col-xs-12 no-padding"
PRODUCT_STOCK_CLASS_NAME = "product-stock"

# Read the page contents and get structured data using beautiful soup
data = bSoup(requests.get(URL).text, "html.parser")

# Find all the item containers
containers = data.findAll("div", {"class", "product"})


def get_features_list(div):
    """
    Iterates the supplied div element and creates pipe-separated string out of each list item in it
    :return: pipe-separated string from <li/>
    """
    concat_features = ""
    for i in div.findAll("li", {}):
        concat_features = i.text + " | " + concat_features
    concat_features = concat_features[:-3] if concat_features.endswith(" | ") else concat_features
    return concat_features if len(concat_features) > 0 else "-"


# Write contents to a csv file
if len(containers) > 0:
    filename = "scrapped_products.csv"
    f = open(filename, "w")
    headers = "Title, Brand, Description, Features, Price\n"
    f.write(headers)

    # Get item information for each item in container
    for item in containers:
        # Only pick items that are available in stock
        stockDiv = item.find("div", {"class", PRODUCT_STOCK_CLASS_NAME})
        if "out" not in stockDiv.findAll("span", {})[1].text.lower():
            titleDiv = item.find("div", {"class", PRODUCT_TITLE_CLASS_NAME})
            descriptionDiv = item.find("div", {"class", PRODUCT_DESCRIPTION_CLASS_NAME})
            priceDiv = item.find("div", {"class", PRODUCT_PRICE_CLASS_NAME})
            featuresDiv = item.find("ul", {"class", PRODUCT_FEATURES_CLASS_NAME})

            title = titleDiv.h4.a.text
            brand = item.find("span", {"class", "product-data"}).text
            description = descriptionDiv.findAll("p", {})[1].text
            features = get_features_list(featuresDiv)
            price = priceDiv.span.text

            print(
                title.replace(",", "|") + ", " +
                brand.replace(",", "|") + ", " +
                description.replace(",", "|") + ", " +
                features.replace(",", "|") + ", " +
                price + "\n"
            )

    f.close()
    print("Items updated at " + strftime("%a, %d %b %Y %X +0000", gmtime()))
