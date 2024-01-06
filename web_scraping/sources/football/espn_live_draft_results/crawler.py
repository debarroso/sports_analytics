from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import datetime, time, pathlib, csv, platform, os


delimiter = "\\" if platform.system() == "Windows" else "/"


class EspnLiveDraftResultsCrawler:

    def __init__(self):

        if platform.system == "Windows":
            self.delimiter = "\\"
        else:
            self.delimiter = "/"
        
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://fantasy.espn.com/football/livedraftresults"

    def initialize_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        firefox_options.set_preference("general.useragent.override", user_agent)

        web_scraping_path = f"{pathlib.Path(__file__).parent.parent.parent.parent.resolve()}"
        driver = webdriver.Firefox(options=firefox_options)
        driver.install_addon(f"{web_scraping_path}{self.delimiter}tools{self.delimiter}selenium{self.delimiter}extensions{self.delimiter}uBlock0.xpi")
        
        driver.maximize_window()
        return driver

    def crawl(self):
        self.driver.get(self.source_url)
        time.sleep(8)
        nav = self.driver.find_elements(By.TAG_NAME, "nav")
        buttons = nav[2].find_elements(By.TAG_NAME, "button")
        next_button = buttons[1]

        rankings = []
        count = 1
        while next_button.is_enabled():
            rankings += self.get_table_stats()
            next_button.click()
            time.sleep(3)
            count += 1
            if count > 10:
                break

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
        file_path = f"{str(self.current_path).replace('web_scraping', 'datalake')}{delimiter}unprocessed"
        file_name = f"espn_live_draft_results_{timestamp.replace(':', '')}.csv"

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        if not os.path.exists(f"{file_path.replace('unprocessed', 'processed')}"):
            os.makedirs(f"{file_path.replace('unprocessed', 'processed')}")

        with open(f"{file_path}{delimiter}{file_name}", mode='w', encoding='utf-8', newline='') as fp:
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
    