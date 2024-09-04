from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from library.classes.base_crawler import BaseCrawler
from selenium.webdriver.common.by import By
import datetime
import pathlib
import time
import csv


class EspnLiveDraftTrendsCrawler(BaseCrawler):

    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent,
            crawler_class=self.__class__.__name__,
            headless=headless,
        )
        self.data = None
        self.source_url = "https://fantasy.espn.com/football/livedraftresults"
        self.today = datetime.date.today()

    def crawl(self):
        self.logger.info(f"Crawling source: {self.source_url}")
        self.driver.get(self.source_url)

        # wait until table content loads/ is clickable
        WebDriverWait(self.driver, 60).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "Table__TBODY"))
        )

        # get next page button
        nav = self.driver.find_elements(By.TAG_NAME, "nav")
        buttons = nav[2].find_elements(By.TAG_NAME, "button")
        next_button = buttons[1]

        rankings = []

        for page_number in range(1, 11):
            rankings += self.get_table_stats(page_number)

            if page_number < 10:
                next_button.click()

        self.data = rankings

    def get_table_stats(self, page_number):
        header_dict = {
            0: "rank",
            1: "player",
            2: "adp",
            3: "adp_seven_day_trend",
            4: "avg_salary",
            5: "salary_seven_day_trend",
            6: "percent_rostered",
        }

        table = self.driver.find_element(By.TAG_NAME, "tbody")
        rankings = []
        rows = table.find_elements(By.TAG_NAME, "tr")

        # validate that the rank is correct for the page number if not, sleep and try again
        attempt = 0
        while rows[0].find_elements(By.TAG_NAME, "td")[0].text != str(
            (page_number - 1) * 50 + 1
        ):
            self.random_sleep()
            rows = table.find_elements(By.TAG_NAME, "tr")
            attempt += 1

            # if we tried 3 times, something's wrong, raise an exception
            if attempt == 3:
                self.logger.error("Slept 3 times but rank hasn't loaded. Exiting...")
                raise Exception()

        for row in rows:
            row_dict = {
                header_dict[i]: element.text
                for i, element in enumerate(row.find_elements(By.TAG_NAME, "td"))
            }

            rankings.append(row_dict)

        return rankings

    def save_to_datalake(self):
        file_name = f"espn_live_draft_trends_{self.today}.csv"
        file_path = self.unprocessed_path / file_name

        self.logger.info(f"Saving data to {file_path}")
        with file_path.open(mode="w", encoding="utf-8", newline="") as fp:
            fieldnames = [
                "rank",
                "player",
                "team",
                "position",
                "adp",
                "adp_seven_day_trend",
                "avg_salary",
                "salary_seven_day_trend",
                "percent_rostered",
            ]

            csv_writer = csv.DictWriter(fp, fieldnames=fieldnames)
            csv_writer.writeheader()

            for row in self.data:
                player_string_split = row["player"].split("\n")
                row["player"] = player_string_split[0]
                row["team"] = player_string_split[-2]
                row["position"] = player_string_split[-1]

                csv_writer.writerow(row)


if __name__ == "__main__":
    run_start = time.perf_counter()
    with EspnLiveDraftTrendsCrawler(headless=False) as crawler:
        crawler.crawl()
        crawler.save_to_datalake()
        crawler.logger.info(f"Crawl run time = {time.perf_counter() - run_start}")
