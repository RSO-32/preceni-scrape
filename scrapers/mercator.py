from os import environ
from typing import Any
from scrapers.product import Product
from datetime import datetime
import requests
import time
from scrapers.product import Product
from config import Config


class MercatorScraper:
    enabled = False
    current_app: Any

    @staticmethod
    def scrape(*args, **kwargs):
        MercatorScraper.current_app = kwargs["app"]
        MercatorScraper.current_app.logger.info("Starting Mercator scraper")

        offset = 0
        from_ = 0

        def extract_products(products_response) -> list[Product]:
            products = []

            for product in products_response:
                if "itemId" not in product:
                    MercatorScraper.current_app.logger.info(f"Skipping promotional image")
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
                        image_url=product["mainImageSrc"],
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

            url = f"{Config.mercator_api_endpoint}?limit={limit}&offset={offset}&from={from_}"

            try:
                MercatorScraper.current_app.logger.info(f"Requesting {url}")
                response = requests.get(url)
                response.raise_for_status()

                MercatorScraper.current_app.logger.info(f"Extracting products")
                products = extract_products(response.json())
                MercatorScraper.current_app.logger.info(f"Found {len(products)} products")

                Product.send_products(products, MercatorScraper.current_app.logger)

            except Exception as e:
                MercatorScraper.current_app.logger.error("Received HTTP error, opening circuit breaker")

                fail_count = 0

                while True:
                    if fail_count == 3:
                        MercatorScraper.current_app.logger.error("Permanently opening circuit breaker")
                        MercatorScraper.enabled = False
                        break

                    MercatorScraper.current_app.logger.info("Waiting before retrying")
                    time.sleep(int(environ.get("REQUESTS_DELAY")) * 2)

                    MercatorScraper.current_app.logger.info("Half-opening circuit breaker")

                    try:
                        response = requests.get(Config.mercator_api_endpoint)

                        if response.status_code == 200:
                            MercatorScraper.current_app.logger.info("API is up, closing circuit breaker")
                            break
                        else:
                            MercatorScraper.current_app.logger.error("API still down")
                            fail_count += 1
                    except Exception as e:
                        MercatorScraper.current_app.logger.error("API still down")
                        fail_count += 1

            offset += 1
            from_ = offset * limit
            time.sleep(int(environ.get("REQUESTS_DELAY")))
