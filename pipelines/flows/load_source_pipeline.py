from prefect import flow, task
from prefect.states import Completed, Failed
import importlib
import pathlib
import inspect
import glob
import json
import time
import os


def import_class_from_file(file_path):
    spec = importlib.util.spec_from_file_location(
        pathlib.Path(file_path).stem, file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return [
        member[1]
        for member in inspect.getmembers(module, inspect.isclass)
        if member[1].__module__ == module.__name__
    ][0]


@task(name="Crawling Source", retries=3)
def crawl_data_source(source_slug):
    run_start = time.perf_counter()

    # import the crawler class
    base_path = pathlib.Path(__file__).parents[2] / "web_scraping"
    pattern = os.path.join(base_path, "**", source_slug, "**", "crawler.py")
    crawler_class = import_class_from_file(glob.glob(pattern, recursive=True)[0])

    with crawler_class(headless=False) as crawler:
        crawler.crawl()
        crawler.save_to_datalake()
        crawler.logger.info(f"Crawl run time = {time.perf_counter() - run_start}")


@task(name="Processing New Data", retries=3)
def process_new_data(source_slug):
    run_start = time.perf_counter()

    # import the parser class
    base_path = pathlib.Path(__file__).parents[2] / "web_scraping"
    pattern = os.path.join(base_path, "**", source_slug, "**", "parser.py")
    parser_class = import_class_from_file(glob.glob(pattern, recursive=True)[0])

    parser = parser_class()
    parser.parse()
    parser.save_parsed_data()
    parser.logger.info(f"Parse run time = {time.perf_counter() - run_start}")


@task(name="Uploading New Data", retries=3)
def upload_new_data(source_slug):
    run_start = time.perf_counter()

    # import the db_handler class
    base_path = pathlib.Path(__file__).parents[2] / "database"
    pattern = os.path.join(base_path, "**", source_slug, "**", "database_handler.py")
    db_handler_class = import_class_from_file(glob.glob(pattern, recursive=True)[0])

    db_handler = db_handler_class()
    db_handler.upload_parsed_data()
    db_handler.logger.info(
        f"DB connection run time = {time.perf_counter() - run_start}"
    )


@flow(name="Load Source Data Pipeline")
def load_source_data_pipeline(source_slug=None):
    if source_slug is None:
        return Failed(message="No source slug provided")

    crawl_data_source(source_slug)
    process_new_data(source_slug)
    upload_new_data(source_slug)

    return Completed(message="Pipeline completed successfully")


if __name__ == "__main__":
    flow_file = pathlib.Path(__file__)
    deployments_file = flow_file.parents[1] / "deployments" / f"{flow_file.stem}.json"

    with deployments_file.open("r") as f:
        deployments = json.load(f)

    for deployment in deployments:
        load_source_data_pipeline.serve(
            name=deployment["name"],
            tags=deployment["tags"],
            parameters=deployment["parameters"],
            cron=deployment["cron"],
        )
