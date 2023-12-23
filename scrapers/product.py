from dataclasses import dataclass
from datetime import datetime
import requests
import json
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
    image_url: str

    def toJSON(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "seller_product_id": self.seller_product_id,
            "seller_product_name": self.seller_product_name,
            "image_url": self.image_url,
            "price": self.price,
            "categories": self.categories,
            "brand": self.brand,
            "seller": self.seller,
        }

    @staticmethod
    def send_products(products: list, logger):
        logger.info(f"Sending {len(products)} products")

        url = environ.get("DODAJ_IZDELEK_ENDPOINT")
        headers = {"content-type": "application/json"}

        try:
            data = [product.toJSON() for product in products]
            response = requests.put(url, data=json.dumps(data), headers=headers)
            logger.info(f"Response: {response.status_code}")
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            return
