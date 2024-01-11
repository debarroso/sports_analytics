from selenium.webdriver.common.by import By
import time
import pathlib
import os
import datetime
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_crawler import BaseCrawler


class ProFootballRefGamesCrawler(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://www.pro-football-reference.com"
    
    def crawl(self):
        self.links = self.get_boxscores(2023, 2024)

    def get_boxscores(self, begin=2023, end=2024):
        boxscores = []
        for year in range(begin, end):

            self.random_sleep()
            self.driver.get(f"{self.source_url}/years/{year}/games.htm")
            elements = self.driver.find_elements(By.LINK_TEXT, "boxscore")

            boxscores += [element.get_attribute("href") for element in elements]

        return boxscores

    def get_game_date(self, link):
        game_id = link.split("/")[-1][:-4]
        return f"{game_id[0:4]}-{game_id[4:6]}-{game_id[6:8]}"

    def save_to_datalake(self, limit=5):
        for link in self.links:
            today = datetime.date.today()
            date_string = self.get_game_date(link)
            year = int(date_string.split("-")[0])
            month = int(date_string.split("-")[1])
            day = int(date_string.split("-")[2])
            game_date = datetime.date(year, month, day)

            if today - datetime.timedelta(days=3) >= game_date:
                file_name = link.split('/')[-1]
                file_path = f"{str(self.current_path).replace('web_scraping', 'datalake')}{self.delimiter}unprocessed"
                full_path = f"{file_path}{self.delimiter}{file_name}"

                if not os.path.exists(file_path):
                    os.makedirs(file_path)

                if not os.path.exists(file_path.replace("unprocessed", "processed")):
                    os.makedirs(file_path.replace("unprocessed", "processed"))

                if pathlib.Path(full_path).is_file():
                    continue
                elif pathlib.Path(full_path.replace("unprocessed", "processed")).is_file():
                    continue

                print(file_name)

                self.random_sleep()
                self.driver.get(link)
                
                with open(full_path, mode='w', encoding='utf-8') as fp:
                    fp.write(self.driver.page_source)

                time.sleep(limit)

        self.driver.close()


if __name__ == "__main__":
    crawler = ProFootballRefGamesCrawler()
    crawler.crawl()
    crawler.save_to_datalake()
    