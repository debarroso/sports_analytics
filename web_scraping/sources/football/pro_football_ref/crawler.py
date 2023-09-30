from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, pathlib


class ProFootballRefCrawler:

    def __init__(self):
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://www.pro-football-reference.com"

    def initialize_driver(self):
        firefox_options = Options()
        # firefox_options.add_argument("--headless")
        firefox_options.add_argument("-private")
        return webdriver.Firefox(options=firefox_options)
    
    def crawl(self):
        self.links = self.get_boxscores(2023, 2024)
        [print(link) for link in self.links]

    def get_boxscores(self, begin=2023, end=2024):
        boxscores = []
        for year in range(begin, end):

            self.driver.get(f"{self.source_url}/years/{year}/games.htm")
            elements = self.driver.find_elements_by_link_text("boxscore")

            boxscores += [element.get_attribute("href") for element in elements]

        return boxscores

    def save_to_datalake(self, limit=5):
        for link in self.links:
            file_path = f"{str(self.current_path).replace('web_scraping', 'datalake')}\\{link.split('/')[-1]}"

            if pathlib.Path(file_path).is_file():
                continue

            self.driver.get(link)
            with open(file_path, mode='w', encoding='utf-8') as fp:
                fp.write(self.driver.page_source)

            time.sleep(limit)


if __name__ == "__main__":
    crawler = ProFootballRefCrawler()
    crawler.crawl()
    crawler.save_to_datalake()