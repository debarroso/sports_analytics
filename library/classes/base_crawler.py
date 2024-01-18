from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
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
            headless=True,
        ):
        self.logger = self.get_logger()
        self.base_path = pathlib.Path(__file__).parents[2].resolve()
        self.crawler_path = crawler_path
        self.crawler_name = crawler_path.parts[-1]
        self.datalake_path = pathlib.Path(str(self.crawler_path).replace('web_scraping', 'datalake'))
        
        self.unprocessed_path = self.datalake_path / "unprocessed"
        self.unprocessed_path.mkdir(parents=True, exist_ok=True)
        
        self.processed_path = self.datalake_path / "processed"
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        self.driver = None
        self.headless = headless
        self.geckodriver_executable = "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"
        self.web_scraping_tools_path = self.base_path / "web_scraping" / "tools"
        self.geckodriver_path = self.web_scraping_tools_path / "selenium" / self.geckodriver_executable
        self.driver_logs_path = self.web_scraping_tools_path / "selenium" / "geckodriver.log"

    def __enter__(self):
        self.driver = self.initialize_driver(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.driver.close()
        except NoSuchWindowException as e:
            self.logger


    def initialize_driver(self, headless=True):
        firefox_service = Service(
            executable_path=str(self.geckodriver_path),
            log_path=str(self.driver_logs_path)
        )

        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")

        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        firefox_options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(options=firefox_options, service=firefox_service)
        driver.install_addon(str(self.web_scraping_tools_path / "selenium" / "extensions" / "uBlock0.xpi"))
        
        driver.maximize_window()
        return driver
    
    def random_sleep(self):
        ranges = [(3, 7), (7, 11), (11, 20)]
        weights = [0.3, 0.6, 0.1]

        selected_range = random.choices(ranges, weights=weights, k=1)[0]
        sleep_time = random.uniform(*selected_range)
        time.sleep(sleep_time)

    def get_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(self.crawler_name)
    
    def get_postgres_connection(self, db_config={}):
        return psycopg2.connect(**db_config)

    def scroll_page_down(self, scroll_duration=0, scroll_length=8):
        total_height = int(self.driver.execute_script("return document.body.scrollHeight"))
        scroll_to = 1
        start = time.perf_counter()

        while total_height > scroll_to:
            self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            scroll_to += scroll_length
            total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

            if scroll_duration > 0:
                if time.perf_counter() - start > scroll_duration:
                    break
    
    def download_raw_http_source(
            self,
            url="",
            save_destination=pathlib.Path(__file__).parent,
            write_mode="w",
            header={}
        ):
        response = requests.get(url=url, headers=header)
        self.logger.info(f"Response Code {response.status_code} for downloading {url}")
        with save_destination.open(save_destination, mode=write_mode) as f:
            f.write(response.content)
