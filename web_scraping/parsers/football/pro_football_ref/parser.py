import pandas as pd
from bs4 import BeautifulSoup
import time, datetime
import pathlib, glob


class ProFootballRefParser():

    def __init__(self, file_name="*", tables_to_extract="all"):
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.datalake_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "sources")
        self.match_files = self.get_files(file_name=file_name)
        self.tables = {
            "game_details": [],
            "team_stats": [],
            "passing_stats": [],
            "rushing_stats": [],
            "receiving_stats": [],
            "defense_stats": [],
            "return_stats": [],
            "kicking_stats": [],
            "punting_stats": [],
            "snap_counts": [],
            "play_by_play": []
        }

    def parse(self):
        for match_file in self.match_files:
            self.soup = self.get_soup(file_name=match_file)
            self.game_id = match_file.split(".")[0].split("\\")[-1]
            self.extract_game_details(file_name=match_file)
            self.extract_team_stats(file_name=match_file)
            passing_stats = self.extract_passing_stats(file_name=match_file)
            rushing_stats = self.extract_rushing_stats(file_name=match_file)
            receiving_stats = self.extract_receiving_stats(file_name=match_file)
            defense_stats = self.extract_defense_stats(file_name=match_file)
            return_stats = self.extract_return_stats(file_name=match_file)
            kicking_stats = self.extract_kicking_stats(file_name=match_file)
            play_by_play = self.extract_play_by_play(file_name=match_file)

    def get_files(self, file_name="*"):
        return glob.glob(f"{self.datalake_path}\\{file_name}")

    def get_soup(self, file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    def clean_header(self, header=[]):
        return [c.replace(' ', '_').lower() for c in header]

    def get_game_date(self, game_id=""):
        return f"{game_id[0:4]}-{game_id[4:6]}-{game_id[6:8]}"

    def get_game_result(self, score, opp_score):
        score = int(score)
        opp_score = int(opp_score)

        if score > opp_score:
            return "win"
        elif score == opp_score:
            return "tie"
        else:
            return "loss"

    def extract_game_details(self, file_name=""):
        game_id = self.game_id
        game_date = self.get_game_date(game_id=self.game_id)
        game_info = pd.read_html(file_name, match="Game Info")
        officials = pd.read_html(file_name, match="Officials")

        game_info_keys = game_info[0]["Game Info"].values.tolist()
        game_info_values = game_info[0]["Game Info.1"].values.tolist()

        officials_keys = officials[0]["Officials"].values.tolist()
        officials_values = officials[0]["Officials.1"].values.tolist()

        game_info_dict = dict(zip(self.clean_header(game_info_keys), game_info_values))
        officials_dict = dict(zip(self.clean_header(officials_keys), officials_values))

        meta_box = self.soup.find("div", attrs={"class": "scorebox_meta"})
        for element in meta_box.find_all("div"):
            if "Start Time" in element.text:
                game_time = element.text.replace("Start Time: ", "")

        game_details = {"game_id": game_id, "game_date": game_date, "game_time": game_time}
        game_details.update({**game_info_dict, **officials_dict})

        self.tables["game_details"].append(game_details)

    def extract_team_stats(self, file_name=""):
        game_id = self.game_id
        game_date = self.get_game_date(game_id=self.game_id)

        scorebox = self.soup.find("div", attrs={"class": "scorebox"})
        away_team = scorebox.find_all("div")[0]
        home_team = scorebox.find_all("div")[8]

        away_team_meta = away_team.find_all("strong")[0]
        away_team_id = away_team_meta.find_all("a")[0].get("href")
        away_team_name = away_team_meta.text.strip()
        away_team_score = away_team.find("div", attrs={"class": "score"}).text
        away_coach = away_team.find("div", attrs={"class": "datapoint"})
        away_coach_id = away_coach.find_all("a")[0].get("href")
        away_coach_name = away_coach.find_all("a")[0].text.strip()
        
        home_team_meta = home_team.find_all("strong")[0]
        home_team_id = home_team_meta.find_all("a")[0].get("href")
        home_team_name = home_team_meta.text.strip()
        home_team_score = home_team.find("div", attrs={"class": "score"}).text
        home_coach = home_team.find("div", attrs={"class": "datapoint"})
        home_coach_id = home_coach.find_all("a")[0].get("href")
        home_coach_name = home_coach.find_all("a")[0].text.strip()

        team_stats = pd.read_html(file_name, match="Team Stats")[0]
        stat_keys = self.clean_header(team_stats.iloc[:,0].values.tolist())
        away_team_stats = team_stats.iloc[:,1].values.tolist()
        home_team_stats = team_stats.iloc[:,2].values.tolist()

        away_team_dict = {
            "game_id": game_id,
            "game_date": game_date,
            "team_id": away_team_id,
            "team_name": away_team_name,
            "team_score": away_team_score,
            "coach_id": away_coach_id,
            "coach_name": away_coach_name,
            "home": False,
            "result": self.get_game_result(away_team_score, home_team_score)
        }

        home_team_dict = {
            "game_id": game_id,
            "game_date": game_date,
            "team_id": home_team_id,
            "team_name": home_team_name,
            "team_score": home_team_score,
            "coach_id": home_coach_id,
            "coach_name": home_coach_name,
            "home": True,
            "result": self.get_game_result(home_team_score, away_team_score)
        }

        away_stats_dict = dict(zip(stat_keys, away_team_stats))
        home_stats_dict = dict(zip(stat_keys, home_team_stats))

        away_team_dict.update(**away_stats_dict)
        home_team_dict.update(**home_stats_dict)
        
        self.tables["team_stats"].append(away_team_dict)
        self.tables["team_stats"].append(home_team_dict)

    def extract_passing_stats(self, file_name=""):
        game_id = self.game_id
        game_date = self.get_game_date(game_id=self.game_id)

        passing_tables = pd.read_html(file_name, match="Passing", extract_links="body")
        basic_passing = passing_tables[0].iloc[:,:11]

        print(basic_passing)

    def extract_rushing_stats(self, file_name=""):
        pass

    def extract_receiving_stats(self, file_name=""):
        pass

    def extract_defense_stats(self, file_name=""):
        pass

    def extract_return_stats(self, file_name=""):
        pass

    def extract_kicking_stats(self, file_name=""):
        pass

    def extract_play_by_play(self, file_name=""):
        pass

    def save_parsed_data(self):
        for table in self.tables:
            pass


if __name__ == "__main__":
    [ProFootballRefParser(f).parse() for f in ["202301010atl.htm", "201009120pit.htm"]]
    # parser = ProFootballRefParser()
    # parser.parse()