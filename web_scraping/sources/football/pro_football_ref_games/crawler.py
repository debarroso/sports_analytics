from selenium.webdriver.common.by import By
import pathlib
import datetime
import sys


project_path = pathlib.Path(__file__).resolve().parents[4]
sys.path.append(f"{project_path}/")
from library.classes.base_crawler import BaseCrawler


class ProFootballRefGamesCrawler(BaseCrawler):

    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent,
            headless=headless
        )
        self.logger = self.get_logger()
        self.source_url = "https://www.pro-football-reference.com"
        self.today = datetime.date.today()
    
    def crawl(self, begin=2023, end=2024):
        boxscores = []
        for year in range(begin, end):

            self.random_sleep()
            self.driver.get(f"{self.source_url}/years/{year}/games.htm")
            elements = self.driver.find_elements(By.LINK_TEXT, "boxscore")

            boxscores += [element.get_attribute("href") for element in elements]

        self.links = boxscores

    def get_game_date(self, link):
        game_id = link.split("/")[-1][:-4]
        year = int(game_id[0:4])
        month = int(game_id[4:6])
        day = int(game_id[6:8])
        return datetime.date(year, month, day)

    def save_to_datalake(self):
        for link in self.links:
            game_date = self.get_game_date(link)

            if self.today - datetime.timedelta(days=3) < game_date:
                continue
            
            file_name = link.split('/')[-1]
            
            unprocessed_file_path = self.unprocessed_path / file_name
            processed_file_path = self.processed_path / file_name
            
            if unprocessed_file_path.is_file():
                continue
            elif processed_file_path.is_file():
                continue
            
            self.logger.info(f"Saving {file_name} to datalake")
            self.random_sleep()
            self.driver.get(link)
            
            with unprocessed_file_path.open(mode='w', encoding='utf-8') as fp:
                fp.write(self.driver.page_source)

            self.random_sleep()


if __name__ == "__main__":
    with ProFootballRefGamesCrawler() as crawler:
        crawler.crawl()
        crawler.save_to_datalake()
