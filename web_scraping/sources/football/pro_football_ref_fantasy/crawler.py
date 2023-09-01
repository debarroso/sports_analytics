from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, pathlib


class ProFootballRefFantasyCrawler:

    def __init__(self):
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()

    def initialize_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("-private")
        return webdriver.Firefox(options=firefox_options)
    
    def crawl(self):
        self.links = []
        for year in range(2023, 2024):
            self.links.append(f"https://www.pro-football-reference.com/years/{year}/fantasy.htm")        

    def save_to_datalake(self, limit=5):
        for link in self.links:
            file_name = f"fantasy_rankings_{link.split('/')[-2]}"
            file_path = f"{str(self.current_path).replace('web_scraping', 'datalake')}\\{file_name}.html"

            if pathlib.Path(file_path).is_file():
                continue

            self.driver.get(link)
            with open(file_path, mode='w', encoding='utf-8') as fp:
                fp.write(self.driver.page_source)

            time.sleep(limit)


if __name__ == "__main__":
    crawler = ProFootballRefFantasyCrawler()
    crawler.crawl()
    crawler.save_to_datalake()