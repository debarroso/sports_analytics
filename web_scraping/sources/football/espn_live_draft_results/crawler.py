from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import datetime, time, pathlib, csv


class EspnLiveDraftResultsCrawler:

    def __init__(self):
        self.driver = self.initialize_driver()
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.source_url = "https://fantasy.espn.com/football/livedraftresults"

    def initialize_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("-private")
        return webdriver.Firefox(options=firefox_options)

    def crawl(self):
        self.driver.get(self.source_url)
        time.sleep(8)
        nav = self.driver.find_elements_by_tag_name("nav")
        buttons = nav[2].find_elements_by_tag_name("button")
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

        table = self.driver.find_element_by_tag_name("tbody")
        rankings = []

        for row in table.find_elements_by_tag_name("tr"):
            row_dict = {}
            elements = row.find_elements_by_tag_name("td")
            count = 0

            for element in elements:
                row_dict[header_dict[count]] = element.text
                count += 1
            
            rankings.append(row_dict)

        return rankings

    def save_to_datalake(self):
        timestamp = str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
        file_path = str(self.current_path).replace('web_scraping', 'datalake')
        file_name = f"espn_live_draft_results_{timestamp.replace(':', '')}.csv"

        with open(f"{file_path}\\{file_name}", mode='w', encoding='utf-8', newline='') as fp:
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