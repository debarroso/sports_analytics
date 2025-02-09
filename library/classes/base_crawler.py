from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
import datetime
import psycopg2
import requests
import platform
import pathlib
import logging
import random
import time


class BaseCrawler:

    def __init__(
        self,
        crawler_path,
        crawler_class,
        headless=True,
    ):
        self.base_path = pathlib.Path(__file__).parents[2].resolve()
        self.web_scraping_tools_path = self.base_path / "web_scraping" / "tools"
        self.crawler_path = crawler_path
        self.crawler_name = crawler_path.parts[-1]
        self.crawler_class = crawler_class

        self.datalake_path = pathlib.Path(
            str(self.crawler_path).replace("web_scraping", "datalake")
        )

        self.logger = self.get_logger()
        self.headless = headless

        self.logger.info(
            f"---------- Beginning run of {self.crawler_class} at {datetime.datetime.now()} ----------"
        )

        self.unprocessed_path = self.datalake_path / "unprocessed"
        self.unprocessed_path.mkdir(parents=True, exist_ok=True)

        self.processed_path = self.datalake_path / "processed"
        self.processed_path.mkdir(parents=True, exist_ok=True)

        self.driver = self.initialize_driver(headless=self.headless)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.driver.close()
            self.logger.info(
                f"---------- Completed run of {self.crawler_class} at {datetime.datetime.now()} ----------"
            )
        except NoSuchWindowException:
            self.logger.error(f"Driver window was already closed when exiting class.")
        except Exception as e:
            self.logger.error(str(e))
            raise e

    def get_logger(self):
        file_path = self.base_path / "logs" / f"{self.crawler_name}_pipeline.log"
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

        logging.basicConfig(
            filename=str(file_path),
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger(self.crawler_name)

    def initialize_driver(self, headless=True):
        geckodriver_executable = (
            "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
        )
        geckodriver_path = (
            self.web_scraping_tools_path / "selenium" / geckodriver_executable
        )
        driver_logs_path = self.web_scraping_tools_path / "selenium" / "geckodriver.log"

        self.logger.info("Initializing selenium webdriver")
        firefox_service = Service(
            executable_path=str(geckodriver_path),
            log_path=str(driver_logs_path),
        )

        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")

        firefox_options.add_argument("-private")

        if platform.system() == "Windows":
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
            firefox_options.set_preference("general.useragent.override", user_agent)
        elif platform.system() == "Darwin":
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0"
            firefox_options.set_preference("general.useragent.override", user_agent)

        for attempt in range(1, 4):
            try:
                driver = webdriver.Firefox(
                    options=firefox_options, service=firefox_service
                )
                driver.install_addon(
                    str(
                        self.web_scraping_tools_path
                        / "selenium"
                        / "extensions"
                        / "uBlock0.xpi"
                    )
                )
                driver.maximize_window()
                return driver

            except WebDriverException as e:
                if attempt == 3:
                    self.logger.error("Failed to initialize driver after 3 attempts")
                    self.logger.error(str(e))
                    raise e

    @staticmethod
    def random_sleep(ranges=None, weights=None):
        if weights is None:
            weights = [0.3, 0.6, 0.1]

        if ranges is None:
            ranges = [(3, 5), (5, 8), (8, 12)]

        selected_range = random.choices(ranges, weights=weights, k=1)[0]
        sleep_time = random.uniform(*selected_range)
        time.sleep(sleep_time)

    @staticmethod
    def get_postgres_connection(**kwargs):
        return psycopg2.connect(**kwargs)

    def scroll_page_down(self, scroll_duration=0, scroll_length=8):
        total_height = int(
            self.driver.execute_script("return document.body.scrollHeight")
        )
        scroll_to = 1
        start = time.perf_counter()

        while total_height > scroll_to:
            self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            scroll_to += scroll_length
            total_height = int(
                self.driver.execute_script("return document.body.scrollHeight")
            )

            if scroll_duration > 0:
                if time.perf_counter() - start > scroll_duration:
                    break

    def download_url_content(
        self,
        url="",
        save_destination=pathlib.Path(__file__).parents[2].resolve(),
        header=None,
    ):
        if header is None:
            header = {}

        response = requests.get(url=url, headers=header)
        self.logger.info(f"Response code {response.status_code} for downloading {url}")
        with save_destination.open(mode="wb") as fp:
            fp.write(response.content)
