import logging
import sys
import requests
import time
from dataclasses import dataclass
import datetime
import json
from dotenv import load_dotenv
from os.path import join, dirname
from os import environ

@dataclass
class Product:
    timestamp: datetime
    seller_product_id: str
    seller_product_name: str
    price: float
    categories: list[str]
    brand: str
    seller: str

    def toJSON(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "seller_product_id": self.seller_product_id,
            "seller_product_name": self.seller_product_name,
            "price": self.price,
            "categories": self.categories,
            "brand": self.brand,
            "seller": self.seller,
        }


def send_products(products: list[Product]):
    logging.info(f"    Sending {len(products)} products")

    url = {environ.get("DODAJ_IZDELEK_ENDPOINT")}
    headers = {"content-type": "application/json"}

    try:
        data = [product.toJSON() for product in products]
        response = requests.put(url, data=json.dumps(data), headers=headers)
        logging.info(f"      Response: {response.status_code}")
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return


def scrape_mercator(offset=0, from_=0):
    def extract_products(products_response) -> list[Product]:
        products = []

        for product in products_response:
            if "itemId" not in product:
                logging.info(f"    Skipping promotional image")
                continue

            categories = [
                product["data"]["category1"],
                product["data"]["category2"],
                product["data"]["category3"],
            ]

            products.append(
                Product(
                    timestamp=datetime.datetime.now(),
                    seller_product_id=product["itemId"],
                    seller_product_name=product["short_name"],
                    price=product["data"]["current_price"],
                    categories=categories,
                    brand=product["data"]["brand_name"],
                    seller="Mercator",
                )
            )

        return products

    logging.info("Scraping Mercator")
    limit = 80

    while True:
        url = f"https://trgovina.mercator.si/market/products/browseProducts/getProducts?limit={limit}&offset={offset}&from={from_}"

        try:
            logging.info(f"  Requesting {url}")
            response = requests.get(url)
            response.raise_for_status()

            logging.info(f"    Extracting products")
            products = extract_products(response.json())
            logging.info(f"    Found {len(products)} products")

            send_products(products)

        except requests.exceptions.HTTPError as e:
            logging.error(e)
            continue

        offset += 1
        from_ = offset * limit
        time.sleep(environ.get("REQUESTS_DELAY"))


def scrape_tus():
    logging.info("Scraping Tuš")


def scrape_spar():
    logging.info("Scraping Spar")


if __name__ == "__main__":
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    scrape_mercator()
    scrape_tus()
    scrape_spar()
