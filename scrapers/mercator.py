import logging
from os import environ
from typing import Any
from scrapers.product import Product
from datetime import datetime
import requests
import time
from scrapers.product import Product


class MercatorScraper:
    enabled = False
    current_app: Any

    @staticmethod
    def scrape(*args, **kwargs):
        logging.info("Starting Mercator scraper")

        MercatorScraper.current_app = kwargs["app"]

        offset = 0
        from_ = 0

        def extract_products(products_response) -> list[Product]:
            products = []

            for product in products_response:
                if "itemId" not in product:
                    logging.info(f"Skipping promotional image")
                    continue

                categories = [
                    product["data"]["category1"],
                    product["data"]["category2"],
                    product["data"]["category3"],
                ]

                products.append(
                    Product(
                        timestamp=datetime.now(),
                        seller_product_id=product["itemId"],
                        seller_product_name=product["short_name"],
                        price=product["data"]["current_price"],
                        categories=categories,
                        brand=product["data"]["brand_name"],
                        seller="Mercator",
                    )
                )

            return products

        limit = 80

        while MercatorScraper.enabled:
            MercatorScraper.current_app.logger.info("Scraping Mercator")

            url = f"https://trgovina.mercator.si/market/products/browseProducts/getProducts?limit={limit}&offset={offset}&from={from_}"

            try:
                MercatorScraper.current_app.logger.info(f"Requesting {url}")
                response = requests.get(url)
                response.raise_for_status()

                MercatorScraper.current_app.logger.info(f"Extracting products")
                products = extract_products(response.json())
                MercatorScraper.current_app.logger.info(f"Found {len(products)} products")

                Product.send_products(products, MercatorScraper.current_app.logger)

            except requests.exceptions.HTTPError as e:
                MercatorScraper.current_app.logger.error(e)
                continue

            offset += 1
            from_ = offset * limit
            time.sleep(int(environ.get("REQUESTS_DELAY")))
