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
        self.rankings_cache = set()
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
            rankings += self.get_table_stats()

            if page_number < 10:
                next_button.click()

        self.data = rankings

    def get_table_stats(self):
        self.random_sleep()
        self.scroll_page_down(scroll_length=2)
        header_keys = [
            "rank",
            "player",
            "adp",
            "adp_seven_day_trend",
            "avg_salary",
            "salary_seven_day_trend",
            "percent_rostered",
        ]

        table = self.driver.find_element(By.TAG_NAME, "tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")
        rankings = []
        cache_values = set()

        for row in rows:
            cell_texts = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
            row_dict = dict(zip(header_keys, cell_texts))
            row_cache = str({k: v for k, v in row_dict.items() if k != "rank"})

            if row_cache in self.rankings_cache:
                print(row_cache, "is already cached")
                continue
            else:
                cache_values.add(row_cache)
            rankings.append(row_dict)

        # if there's a duplicate entry, the page hasn't finished loading. try again.
        if len(rankings) != len(rows):
            return self.get_table_stats()
        else:
            for value in cache_values:
                self.rankings_cache.add(value)
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
