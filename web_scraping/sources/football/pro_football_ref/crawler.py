import requests
from bs4 import BeautifulSoup
import pathlib
import datetime
import time

class ProFootballRefCrawler:

    def __init__(self):
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://www.pro-football-reference.com"

    def crawl(self):
        self.links = self.get_boxscores(2023, 2024)
        [print(link) for link in self.links]

    def get_boxscores(self, begin=2023, end=2024):
        boxscores = []
        for year in range(begin, end):
            response = requests.get(f"{self.source_url}/years/{year}/games.htm")
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.find_all("a", text="boxscore")

            boxscores += [self.source_url + element.get('href') for element in elements]
        return boxscores

    def get_game_date(self, link):
        game_id = link.split("/")[-1][:-4]
        return f"{game_id[0:4]}-{game_id[4:6]}-{game_id[6:8]}"

    def save_to_datalake(self, limit=5):
        for link in self.links:
            today = datetime.date.today()
            date_string = self.get_game_date(link)
            year, month, day = map(int, date_string.split("-"))
            game_date = datetime.date(year, month, day)

            if today - datetime.timedelta(days=3) >= game_date:
                file_path = f"{str(self.current_path).replace('web_scraping', 'datalake')}\\{link.split('/')[-1]}"

                if pathlib.Path(file_path).is_file():
                    continue

                response = requests.get(link)
                with open(file_path, mode='w', encoding='utf-8') as fp:
                    fp.write(response.text)

                time.sleep(limit)


if __name__ == "__main__":
    crawler = ProFootballRefCrawler()
    crawler.crawl()
    crawler.save_to_datalake()
