from datetime import datetime
import pandas as pd
import pathlib
import time
import os
import re
import csv
import sys


project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(f"{project_path}/")
from library.classes.base_parser import BaseParser


class ProFootballRefPlayersParser(BaseParser):

    def __init__(self, glob_string="*"):
        super().__init__(
            parser_path=pathlib.Path(__file__).parent.resolve(),
            glob_string=glob_string
        )
        self.fieldnames = [
            "id",
            "name",
            "position",
            "throws",
            "height",
            "weight_lb",
            "height_cm",
            "weight_kg",
            "date_of_birth",
            "college",
            "draft_pick",
            "hof_monitor",
            "forty_yd",
            "bench",
            "broad_jump",
            "shuttle",
            "three_cone",
            "vertical"
        ]
        self.data = []

    def parse(self):
        for player_file in self.files:
            start_time = time.perf_counter()
            self.soup = self.get_soup(file_name=player_file)
            self.soup_str = str(self.soup)
            self.extract_player_details(player_file)
            print(f"Processing file {player_file.split(self.delimiter)[-1]} took {time.perf_counter() - start_time}")
            os.rename(player_file, player_file.replace("unprocessed", "processed"))

    def extract_player_details(self, file_name=""):
        player_data = {}
        player_data["id"] = file_name.split(self.delimiter)[-1][10:].replace(".htm", "")
        info_div = self.soup.find("div", id="info")
        player_data["name"] = info_div.find("h1").text.strip()
        
        player_string = ""
        for p in info_div.find_all("p"):
            field_text = " ".join([child.text.strip() for child in p.children])
            player_string += f"{field_text}\n"

        # Extracting and storing the required information
        position_search = re.search(r'Position\s*:\s*(\w+)', player_string)
        if position_search:
            player_data["position"] = position_search.group(1)
            if player_data["position"] == "QB":
                throws_search = re.search(r'Throws:\s*(\w+)', player_string)
                if throws_search:
                    player_data["throws"] = throws_search.group(1)

        height_weight_search = re.search(r'(\d+-\d+)\s*,\s*(\d+)lb\s*\((\d+cm),\s*(\d+kg)\)', player_string)
        if height_weight_search:
            player_data["height"] = height_weight_search.group(1)
            player_data["weight_lb"] = int(height_weight_search.group(2).replace("lb", ""))
            player_data["height_cm"] = int(height_weight_search.group(3).replace("cm", ""))
            player_data["weight_kg"] = int(height_weight_search.group(4).replace("kg", ""))

        dob_search = re.search(r'Born:\s*(.*)', player_string)
        if dob_search:
            date_string = dob_search.group(1).replace('\xa0', ' ').split("(Age")[0].strip()
            player_data["date_of_birth"] = datetime.strptime(date_string, "%B %d, %Y").strftime("%Y-%m-%d")

        college_search = re.search(r'College\s*:\s*(.*?)\s*\(', player_string)
        if college_search:
            player_data["college"] = college_search.group(1)

        draft_search = re.search(r'Draft\s*:\s*.*\((\d+)(?:st|nd|rd|th)\s*overall\)', player_string)
        if draft_search:
            player_data["draft_pick"] = int(draft_search.group(1))
            
        hof_monitor = self.soup.find("a", href="/about/hof_monitor.htm")
        if hof_monitor is not None:
            player_data["hof_monitor"] = hof_monitor.parent.b.text
        
        try:
            combine_df = pd.read_html(file_name, match="Combine Measurements")
            
            if len(combine_df) > 0:
                combine_df = combine_df.pop().fillna("")
            
                df_map = {
                    "forty_yd": "40yd",
                    "bench": "Bench",
                    "broad_jump": "Broad Jump",
                    "shuttle": "Shuttle",
                    "three_cone": "3Cone",
                    "vertical": "Vertical"
                }

                for key in df_map.keys():
                    if combine_df[df_map[key]].values[0] != "":
                        player_data[key] = combine_df[df_map[key]].values[0]

        except ValueError as e:
            if str(e) == "No tables found matching pattern 'Combine Measurements'":
                print(f"No combine measurements for {file_name.split(self.delimiter)[-1]}")
            else:
                raise e

        self.data.append(player_data)
        
    def save_parsed_data(self):
        with open(f"{self.parsed_path}{self.delimiter}players.csv", mode="w") as out_file:
            csv_writer = csv.DictWriter(out_file, fieldnames=self.fieldnames)
            csv_writer.writeheader()
            for record in self.data:
                csv_writer.writerow(record)


if __name__ == "__main__":
    run_start = time.perf_counter()
    parser = ProFootballRefPlayersParser()
    parser.parse()
    parser.save_parsed_data()
    print(f"Total run time = {time.perf_counter() - run_start}")
