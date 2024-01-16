from selenium.webdriver.common.by import By
import datetime
import pathlib
import time
import csv
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_crawler import BaseCrawler


class EspnLiveDraftTrendsCrawler(BaseCrawler):

    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent
        )      
        self.driver = self.initialize_driver(headless=headless)
        self.source_url = "https://fantasy.espn.com/football/livedraftresults"
        self.today = datetime.date.today()

    def crawl(self):
        self.driver.get(self.source_url)
        time.sleep(10)

        nav = self.driver.find_elements(By.TAG_NAME, "nav")
        buttons = nav[2].find_elements(By.TAG_NAME, "button")
        next_button = buttons[1]

        rankings = []
        count = 1
        while next_button.is_enabled():
            rankings += self.get_table_stats()
            
            count += 1
            if count > 10:
                break

            next_button.click()
            self.random_sleep()

        self.data = rankings
        self.driver.close()

    def get_table_stats(self):
        header_dict = {
            0: "rank",
            1: "player",
            2: "adp",
            3: "adp_seven_day_trend",
            4: "avg_salary",
            5: "salary_seven_day_trend",
            6: "percent_rostered"
        }

        table = self.driver.find_element(By.TAG_NAME, "tbody")
        rankings = []

        for row in table.find_elements(By.TAG_NAME, "tr"):
            row_dict = {}
            elements = row.find_elements(By.TAG_NAME, "td")
            
            count = 0
            for element in elements:
                row_dict[header_dict[count]] = element.text
                count += 1
            
            rankings.append(row_dict)

        return rankings

    def save_to_datalake(self):
        file_name = f"espn_live_draft_trends_{self.today}.csv"
        file_path = self.unprocessed_path / file_name

        with file_path.open(mode='w', encoding='utf-8', newline='') as fp:
            fieldnames = [
                "rank",
                "player",
                "team",
                "position",
                "adp",
                "adp_seven_day_trend",
                "avg_salary",
                "salary_seven_day_trend",
                "percent_rostered"
            ]

            csv_writer = csv.DictWriter(fp, fieldnames=fieldnames)
            csv_writer.writeheader()

            for row in self.data:
                player_string = row["player"]
                row["player"] = player_string.split("\n")[0]
                row["team"] = player_string.split("\n")[-2]
                row["position"] = player_string.split("\n")[-1]

                csv_writer.writerow(row)


if __name__ == "__main__":
    crawler = EspnLiveDraftTrendsCrawler(headless=False)
    crawler.crawl()
    crawler.save_to_datalake()
    