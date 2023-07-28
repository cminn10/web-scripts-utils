from bs4 import BeautifulSoup
import requests
import re
from typing import List, Optional
import json
from utils.utils import send_email


def get_email_body(product_info: dict) -> str:
    return f'Price of {product_info["name"]} is now ${product_info["price"]}. ' \
           f'Check it out here: {product_info["url"]} \n\n'


def get_price(url: str) -> Optional[float]:
    # Send a GET request to the Amazon product page
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element using the selector
    element = soup.select_one("div.price__regular > span.price-item.price-item--regular")

    # Extract the text or attribute value from the element
    if element:
        price_string = element.get_text().strip()
        match = re.search(r'\d+(?:\.\d+)?', price_string)
        if match is not None:
            price = float(match.group())
            return price
    return None


with open('tracking_products.json', 'r') as f:
    tracking_products = json.load(f)

email_body = ''
for product, info in tracking_products.items():
    product_url = info['url']
    desired_price = info['desired_price']
    current_price = get_price(product_url)
    if current_price is not None and current_price <= desired_price:
        product_info = {
            'name': product,
            'price': current_price,
            'url': product_url
        }
        email_body += get_email_body(product_info)
send_email('HealthyPetAustin Price Alert', email_body)
