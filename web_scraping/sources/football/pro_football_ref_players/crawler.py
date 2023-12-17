from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, pathlib, platform, os
import psycopg2


class ProFootballRefPlayersCrawler:

    def __init__(self):
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://www.pro-football-reference.com"
        
        if platform.system == "Windows":
            self.delimiter = "\\"
        else:
            self.delimiter = "/"

        self.db_config = {
            "dbname": "nfl_statistics",
            "host": "localhost",  # or your database host
            "port": 5432  # default port for PostgreSQL
        }

    def initialize_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("-private")
        return webdriver.Firefox(options=firefox_options)
    
    def crawl(self):
        # Connect to the database
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

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

    def save_to_datalake(self, limit=5):
        print(f"There are {len(self.links)} unique players")
        for link in self.links:
            file_name = link[1:].replace("/", "_")
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

            self.driver.get(f"{self.source_url}{link}")
            with open(full_path, mode='w', encoding='utf-8') as fp:
                fp.write(self.driver.page_source)

            time.sleep(limit)

        self.driver.close()


if __name__ == "__main__":
    crawler = ProFootballRefPlayersCrawler()
    crawler.crawl()
    crawler.save_to_datalake()
    