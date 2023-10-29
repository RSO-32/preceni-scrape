import logging
import sys
import requests
import time
import tomllib
from dataclasses import dataclass


@dataclass
class Product:
    seller_id: str
    name: str
    price: float
    categories: list[str]
    brand: str


def scrape_mercator(config, offset=0, from_=0):
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
                    seller_id=product["itemId"],
                    name=product["short_name"],
                    price=product["data"]["current_price"],
                    categories=categories,
                    brand=product["data"]["brand_name"],
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

        except requests.exceptions.HTTPError as e:
            logging.error(e)
            continue

        offset += 1
        from_ = offset * limit
        time.sleep(config["requests"]["delay"])


def scrape_tus():
    logging.info("Scraping Tuš")


def scrape_spar():
    logging.info("Scraping Spar")


if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    scrape_mercator(config)
    scrape_tus(config)
    scrape_spar(config)
