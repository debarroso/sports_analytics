from selenium.webdriver.common.by import By
import datetime
import pathlib
import time
import csv
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_crawler import BaseCrawler


class EspnLiveDraftResultsCrawler(BaseCrawler):

    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent
        )      
        self.driver = self.initialize_driver(headless=headless)
        self.source_url = "https://fantasy.espn.com/football/livedraftresults"

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
            self.random_sleep()
            
            count += 1
            if count > 10:
                break

            next_button.click()

        self.data = rankings
        self.driver.close()

    def get_table_stats(self):
        header_dict = {
            0: "Rank",
            1: "Player",
            2: "ADP",
            3: "ADP_7_Day_Trend",
            4: "AVG_Salary",
            5: "Salary_7_Day_Trend",
            6: "Percent_Rostered"
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
        timestamp = str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
        file_name = f"espn_live_draft_results_{timestamp.replace(':', '')}.csv"
        file_path = self.unprocessed_path / file_name

        with file_path.open(mode='w', encoding='utf-8', newline='') as fp:
            fieldnames = [
                "Rank",
                "Player",
                "Team",
                "Position",
                "ADP",
                "ADP_7_Day_Trend",
                "AVG_Salary",
                "Salary_7_Day_Trend",
                "Percent_Rostered"
            ]

            csv_writer = csv.DictWriter(fp, fieldnames=fieldnames)
            csv_writer.writeheader()

            for row in self.data:
                player_string = row["Player"]
                row["Player"] = player_string.split("\n")[0]
                row["Team"] = player_string.split("\n")[-2]
                row["Position"] = player_string.split("\n")[-1]

                csv_writer.writerow(row)


if __name__ == "__main__":
    crawler = EspnLiveDraftResultsCrawler()
    crawler.crawl()
    crawler.save_to_datalake()
    