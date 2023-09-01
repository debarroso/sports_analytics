import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import time, pathlib, glob, matplotlib


class ProFootballRefFantasyParser():

    def __init__(self, file_name="*", tables_to_extract="all"):
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.datalake_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "sources")
        self.files = self.get_files(file_name=file_name)

    def parse(self):
        for f in self.files:
            df = pd.read_html(f, match="Fantasy Rankings")[0]
            df.columns = df.columns.get_level_values(1)
            box_df = df[["FantPos", "FantPt"]].dropna()
            box_df = box_df[box_df["FantPt"] != "FantPt"]
            box_df["FantPt"] = box_df["FantPt"].astype(float)
            box_df = box_df[box_df["FantPt"] >= 25]
            box_plt = box_df.boxplot(column="FantPt", by="FantPos")
            plt.show()
            plt.close()

    def get_files(self, file_name="*"):
        return glob.glob(f"{self.datalake_path}\\{file_name}")

    def get_soup(self, file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    def save_parsed_data(self):
        pass


if __name__ == "__main__":
    parser = ProFootballRefFantasyParser("fantasy_rankings_202*.html")
    parser.parse()