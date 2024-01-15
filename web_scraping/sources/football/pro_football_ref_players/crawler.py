from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pathlib
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_crawler import BaseCrawler


class ProFootballRefPlayersCrawler(BaseCrawler):
    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent
        )
        self.logger = self.get_logger()
        self.driver = self.initialize_driver(headless=headless)
        self.source_url = "https://www.pro-football-reference.com"
        self.db_connection = self.get_postgres_connection(
            db_config={
                "dbname": "nfl_statistics",
                "host": "localhost",  # or your database host
                "port": 5432  # default port for PostgreSQL
            }
        )
    
    def crawl(self):
        # get cursor for db
        cursor = self.db_connection.cursor()

        sql_query = f"""
            select distinct player from (
                select player from pro_football_ref_games_parsed.receiving_stats_advanced
                union all
                select player from pro_football_ref_games_parsed.return_stats
                union all
                select player from pro_football_ref_games_parsed.fumble_stats
                union all
                select player from pro_football_ref_games_parsed.rushing_stats_basic
                union all
                select player from pro_football_ref_games_parsed.rushing_stats_advanced
                union all
                select player from pro_football_ref_games_parsed.receiving_stats_basic
                union all
                select player from pro_football_ref_games_parsed.defense_stats_advanced
                union all
                select player from pro_football_ref_games_parsed.defense_stats_basic
                union all
                select player from pro_football_ref_games_parsed.passing_stats_basic
                union all
                select player from pro_football_ref_games_parsed.passing_stats_advanced
                union all
                select player from pro_football_ref_games_parsed.kicking_stats
            ) as t;
        """

        cursor.execute(sql_query)
        results = cursor.fetchall()

        self.links = [row[0].split("^")[1] for row in results]

    def save_to_datalake(self):
        self.logger.info(f"There are {len(self.links)} unique players in the database")
        for link in self.links:
            file_name = link[1:].replace("/", "_")

            unprocessed_file_path = self.unprocessed_path / file_name
            processed_file_path = self.processed_path / file_name
            
            if unprocessed_file_path.is_file():
                continue
            elif processed_file_path.is_file():
                continue

            self.logger.info(f"Processing file: {file_name}")

            self.random_sleep()
            self.driver.get(f"{self.source_url}{link}")

            try:
                element = self.driver.find_element(by=By.ID, value="meta_more_button")
                self.driver.execute_script("arguments[0].click();", element)
            except NoSuchElementException:
                self.logger.info(f"No meta button on page: {link}")

            try:
                element = self.driver.find_element(By.ID, "transactions_toggler")
                self.driver.execute_script("arguments[0].click();", element)
            except NoSuchElementException:
                self.logger.info(f"No transactions link on page: {link}")

            with unprocessed_file_path.open(mode='w', encoding='utf-8') as fp:
                fp.write(self.driver.page_source)

            self.random_sleep()

        self.driver.close()


if __name__ == "__main__":
    crawler = ProFootballRefPlayersCrawler()
    crawler.crawl()
    crawler.save_to_datalake()
    