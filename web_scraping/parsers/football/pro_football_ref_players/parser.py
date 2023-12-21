import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import pathlib, glob, time, platform, os


def flatten_links(cell):
    if cell[1] is None:
        return cell[0]
    else:
        return f"{cell[0]}^{cell[1]}"

class ProFootballRefPlayersParser():

    def __init__(self, file_name="*"):
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.delimiter = "\\" if platform.system() == "Windows" else "/"
        self.datalake_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "sources")
        self.parsed_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "parsed")
        self.files = self.get_files(file_name=file_name)
        if len(self.files) == 0:
            exit()
        self.tables = []

    def parse(self):
        for player_file in self.files:
            start_time = time.perf_counter()
            self.soup = self.get_soup(file_name=player_file)
            self.soup_str = str(self.soup)
            self.extract_player_details(player_file)
            os.rename(player_file, player_file.replace("unprocessed", "processed"))

            print(f"Processing {player_file.split(self.delimiter)[-1]} took {time.perf_counter() - start_time}")

    def get_files(self, file_name="*"):
        return glob.glob(f"{self.datalake_path}{self.delimiter}unprocessed{self.delimiter}{file_name}")

    def get_soup(self, file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    def extract_player_details(self, file_name=""):
        pass

    def save_parsed_data(self):
        pass


if __name__ == "__main__":
    run_start = time.perf_counter()
    parser = ProFootballRefPlayersParser()
    parser.parse()
    parser.save_parsed_data()
    print(f"Total run time = {time.perf_counter() - run_start}")
