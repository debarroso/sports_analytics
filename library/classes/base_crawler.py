from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import pathlib
import platform


class BaseCrawler:

    def __init__(self):
        self.delimiter = "\\" if platform.system() == "Windows" else "/"

    def initialize_driver(self, headless=True):
        web_scraping_path = f"{pathlib.Path(__file__).parent.parent.parent.resolve()}{self.delimiter}web_scraping"
        firefox_service = Service(
            executable_path=f"{web_scraping_path}{self.delimiter}tools{self.delimiter}selenium{self.delimiter}geckodriver",
            log_path=f"{web_scraping_path}{self.delimiter}tools{self.delimiter}selenium{self.delimiter}geckodriver.log"
        )

        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")

        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        firefox_options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(options=firefox_options, service=firefox_service)
        driver.install_addon(f"{web_scraping_path}{self.delimiter}tools{self.delimiter}selenium{self.delimiter}extensions{self.delimiter}uBlock0.xpi")
        
        driver.maximize_window()
        return driver
    