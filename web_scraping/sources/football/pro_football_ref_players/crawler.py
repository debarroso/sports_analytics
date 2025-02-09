from library.classes.base_crawler import BaseCrawler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pathlib
import time


class ProFootballRefPlayersCrawler(BaseCrawler):

    def __init__(self, headless=True):
        super().__init__(
            crawler_path=pathlib.Path(__file__).resolve().parent,
            crawler_class=self.__class__.__name__,
            headless=headless,
        )
        self.links = None
        self.source_url = "https://www.pro-football-reference.com"
        self.db_connection = self.get_postgres_connection(
            **{
                "dbname": "nfl_statistics",
                "host": "localhost",
                "port": 5432,
            }
        )

    def crawl(self):
        self.logger.info(f"Querying postgres for unique players")
        cursor = self.db_connection.cursor()

        sql_query_path = (
            self.base_path
            / "database"
            / "queries"
            / self.crawler_name
            / "get_all_players.sql"
        )
        with sql_query_path.open(mode="r") as f:
            sql_query = f.read()

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

            self.logger.info(f"Getting player page at: {self.source_url}{link}")
            self.driver.get(f"{self.source_url}{link}")

            try:
                element = self.driver.find_element(by=By.ID, value="meta_more_button")
                self.driver.execute_script("arguments[0].click();", element)
            except NoSuchElementException:
                self.logger.warning(f"No meta button on page: {link}")

            try:
                element = self.driver.find_element(By.ID, "transactions_toggler")
                self.driver.execute_script("arguments[0].click();", element)
            except NoSuchElementException:
                self.logger.warning(f"No transactions link on page: {link}")

            self.logger.info(f"Processing file: {file_name}")
            with unprocessed_file_path.open(mode="w", encoding="utf-8") as fp:
                fp.write(self.driver.page_source)

            self.random_sleep()


if __name__ == "__main__":
    run_start = time.perf_counter()
    with ProFootballRefPlayersCrawler() as crawler:
        crawler.crawl()
        crawler.save_to_datalake()
        crawler.logger.info(f"Crawl run time = {time.perf_counter() - run_start}")
