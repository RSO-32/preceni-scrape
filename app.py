from flask import jsonify, current_app
from flask_cors import CORS
from dotenv import load_dotenv
from os.path import join, dirname
from health import Health
from metrics import Metrics
from os import environ
import logging, graypy
from flask_openapi3 import OpenAPI, Info, Tag
from scrapers.mercator import MercatorScraper
import threading

info = Info(title="Preceni scrape", version="1.0.0", description="Preceni scrape API")
app = OpenAPI(__name__, info=info)
CORS(app)  # Enable CORS for all routes

# Logging
graylog_handler = graypy.GELFUDPHandler("logs.meteo.pileus.si", 12201)
environment = "dev" if environ.get("SCRAPE_SERVICE_DEBUG") else "prod"
graylog_handler.setFormatter(
    logging.Formatter(f"preceni-scrape {environment} %(asctime)s %(levelname)s %(name)s %(message)s")
)
app.logger.addHandler(graylog_handler)
app.logger.setLevel(logging.INFO)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


scraper_tag = Tag(name="product", description="Product")
health_tag = Tag(name="health", description="Health and metrics")


@app.get("/scrape/health/live", tags=[health_tag], summary="Health live check")
def health_live():
    app.logger.info("GET: Health live check")
    status, checks = Health.check_health()
    code = 200 if status == "UP" else 503

    return jsonify({"status": status, "checks": checks}), code


@app.put("/scrape/health/test/toggle", tags=[health_tag], summary="Health test toggle")
def health_test():
    app.logger.info("PUT: Health test toggle")
    Health.force_fail = not Health.force_fail

    return Health.checkTest()


@app.put("/scrape/scrapers/mercator/toggle", tags=[scraper_tag], summary="Mercator scraper toggle")
def mercator_scraper_toggle():
    app.logger.info("PUT: Mercator scraper toggle")
    MercatorScraper.enabled = not MercatorScraper.enabled

    if MercatorScraper.enabled:
        scraper_thread = threading.Thread(
            target=MercatorScraper.scrape, kwargs={"app": current_app._get_current_object()}
        )
        scraper_thread.start()

    return jsonify({"enabled": MercatorScraper.enabled})


@app.get("/scrape/metrics", tags=[health_tag], summary="Metrics")
def metrics():
    app.logger.info("GET: Metrics")
    metrics = Metrics.get_metrics()

    response = ""
    for metric in metrics:
        response += f"{metric.name} {metric.value}\n"

    return response


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=environ.get("SCRAPE_SERVICE_PORT"),
        debug=environ.get("SCRAPE_SERVICE_DEBUG"),
    )
