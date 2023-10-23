import pandas as pd
from bs4 import BeautifulSoup
import time, datetime
import pathlib, glob


def flatten_links(cell):
    if cell[1] is None:
        return cell[0]
    else:
        return f"{cell[0]}^{cell[1]}"

class ProFootballRefParser():

    def __init__(self, file_name="*", tables_to_extract="all"):
        self.current_path = pathlib.Path(__file__).parent.resolve()
        self.datalake_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "sources")
        self.match_files = self.get_files(file_name=file_name)
        self.tables = {
            "game_details": [],
            "team_stats": [],
            "passing_stats": {
                "basic": [],
                "advanced": []
            },
            "rushing_stats": {
                "basic": [],
                "advanced": []
            },
            "receiving_stats": {
                "basic": [],
                "advanced": []
            },
            "fumble_stats": [],
            "defense_stats": {
                "basic": [],
                "advanced": []
            },
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
            for stat_type in ["passing", "rushing", "receiving"]:
                self.extract_offensive_stats(stat_type=stat_type, file_name=match_file)
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
        away_team_abbreviation = team_stats.columns.values[1]
        home_team_abbreviation = team_stats.columns.values[2]
        home_team_stats = team_stats.iloc[:,2].values.tolist()

        away_team_dict = {
            "game_id": game_id,
            "game_date": game_date,
            "team_id": away_team_id,
            "team_name": away_team_name,
            "team_abbreviation": away_team_abbreviation,
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
            "team_abbreviation": home_team_abbreviation,
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

    def extract_offensive_stats(self, stat_type, file_name=""):
        game_id = self.game_id
        game_date = self.get_game_date(game_id=self.game_id)

        match_dict = {
            "passing": "Passing",
            "rushing": "Rushing",
            "receiving": "Receiving"
        }

        slice_dict = {
            "passing": [0,1,2,3,4,5,6,7,8,9,10],
            "rushing": [0,1,11,12,13,14],
            "receiving": [0,1,15,16,17,18,19]
        }

        basic_columns_dict = {
            "passing": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Passing_Cmp": "completions",
                "Passing_Att": "attempts",
                "Passing_Yds": "yards",
                "Passing_TD": "touchdowns",
                "Passing_Int": "interceptions",
                "Passing_Sk": "sacked",
                "Passing_Yds.1": "sacked_yards",
                "Passing_Lng": "longest_completion",
                "Passing_Rate": "passer_rating"
            },
            "rushing": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Rushing_Att": "attempts",
                "Rushing_Yds": "yards",
                "Rushing_TD": "touchdowns",
                "Rushing_Lng": "longest_rush",
            },
            "receiving": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Receiving_Tgt": "targets",
                "Receiving_Rec": "receptions",
                "Receiving_Yds": "yards",
                "Receiving_TD": "touchdowns",
                "Receiving_Lng": "longest_reception",
            }
        }

        advanced_columns_dict = {
            "passing": {
                "Player": "player",
                "Tm": "team",
                "Cmp": "completions",
                "Att": "attempts",
                "Yds": "yards",
                "1D": "first_downs",
                "1D%": "first_downs_per_pass_percentage",
                "IAY": "intended_air_yards",
                "IAY/PA": "intended_air_yards_per_pass",
                "CAY": "completed_air_yards",
                "CAY/Cmp": "completed_air_yards_per_completion",
                "CAY/PA": "completed_air_yards_per_attempt",
                "YAC": "yards_after_catch",
                "YAC/Cmp": "yards_after_catch_per_completion",
                "Drops": "drops",
                "Drop%": "drop_percentage_per_attempt",
                "BadTh": "bad_throws",
                "Bad%": "bad_throw_percentage",
                "Sk": "sacked",
                "Bltz": "blitzed",
                "Hrry": "hurried",
                "Hits": "hits",
                "Prss": "times_pressured",
                "Prss%": "percent_pressured_per_dropback",
                "Scrm": "scrambles",
                "Yds/Scr": "yards_per_scramble"
            },
            "rushing": {
                "Player": "player",
                "Tm": "team",
                "Att": "attempts",
                "Yds": "yards",
                "TD": "touchdowns",
                "1D": "first_downs",
                "YBC": "yards_before_contact",
                "YBC/Att": "yards_before_contact_per_attempt",
                "YAC": "yards_after_contact",
                "YAC/Att": "yards_after_contact_per_attempt",
                "BrkTkl": "broken_tackles",
                "Att/Br": "attempts_per_broken_tackle",
            },
            "receiving": {
                "Player": "player",
                "Tm": "team",
                "Tgt": "targets",
                "Rec": "receptions",
                "Yds": "yards",
                "TD": "touchdowns",
                "1D": "first_downs",
                "YBC": "yards_before_catch",
                "YBC/R": "yards_before_catch_per_reception",
                "YAC": "yards_after_catch",
                "YAC/R": "yards_after_catch_per_reception",
                "ADOT": "avg_depth_of_target",
                "BrkTkl": "broken_tackles",
                "Rec/Br": "receptions_per_broken_tackle",
                "Drop": "drops",
                "Drop%": "drop_percentage",
                "Int": "interceptions_when_targeted",
                "Rat": "qb_rating_when_targeted"
            }
        }

        basic_columns_to_convert_dict = {
            "passing": [
                "completions",
                "attempts",
                "yards",
                "touchdowns",
                "interceptions",
                "sacked",
                "sacked_yards",
                "longest_completion",
                "passer_rating"
            ],
            "rushing": [
                "attempts",
                "yards",
                "touchdowns",
                "longest_rush"
            ],
            "receiving": [
                "targets",
                "receptions",
                "yards",
                "touchdowns",
                "longest_reception"
            ]
        }

        advanced_columns_to_convert_dict = {
            "passing": [
                "completions",
                "attempts",
                "yards",
                "first_downs",
                "first_downs_per_pass_percentage",
                "intended_air_yards",
                "intended_air_yards_per_pass",
                "completed_air_yards",
                "completed_air_yards_per_completion",
                "completed_air_yards_per_attempt",
                "yards_after_catch",
                "yards_after_catch_per_completion",
                "drops",
                "drop_percentage_per_attempt",
                "bad_throws",
                "bad_throw_percentage",
                "sacked",
                "blitzed",
                "hurried",
                "hits",
                "times_pressured",
                "percent_pressured_per_dropback",
                "scrambles",
                "yards_per_scramble"
            ],
            "rushing": [
                "attempts",
                "yards",
                "touchdowns",
                "first_downs",
                "yards_before_contact",
                "yards_before_contact_per_attempt",
                "yards_after_contact",
                "yards_after_contact_per_attempt",
                "broken_tackles",
                "attempts_per_broken_tackle"
            ],
            "receiving": [
                "targets",
                "receptions",
                "yards",
                "touchdowns",
                "first_downs",
                "yards_before_catch",
                "yards_before_catch_per_reception",
                "yards_after_catch",
                "yards_after_catch_per_reception",
                "avg_depth_of_target",
                "broken_tackles",
                "receptions_per_broken_tackle",
                "drops",
                "drop_percentage",
                "interceptions_when_targeted",
                "qb_rating_when_targeted"
            ]
        }

        table_keys = {
            "passing": "passing_stats",
            "rushing": "rushing_stats",
            "receiving": "receiving_stats"
        }

        tables = pd.read_html(file_name, match=match_dict[stat_type], extract_links="body")
        basic_table = tables[0].iloc[:, slice_dict[stat_type]]
        basic_table.columns = basic_table.columns.map('_'.join).str.strip('_')
        basic_table = basic_table.rename(columns=basic_columns_dict[stat_type])
        basic_table = basic_table.applymap(flatten_links)

        for column in basic_columns_to_convert_dict[stat_type]:
            basic_table[column] = basic_table[column].apply(pd.to_numeric, errors="coerce")

        if stat_type == "passing":
            condition = basic_table["attempts"] > 0
        elif stat_type == "rushing":
            condition = basic_table["attempts"] > 0
        elif stat_type == "receiving":
            condition = basic_table["targets"] > 0
        basic_table = basic_table[condition]
        self.tables[table_keys[stat_type]]["basic"].append(basic_table)

        print(basic_table)

        if len(tables) == 1:
            return

        advanced_table = tables[1].applymap(flatten_links)
        advanced_table = advanced_table.rename(columns=advanced_columns_dict[stat_type])

        for column in advanced_columns_to_convert_dict[stat_type]:
            advanced_table[column] = advanced_table[column].apply(pd.to_numeric, errors="coerce")

        if stat_type == "passing":
            condition = advanced_table["attempts"] > 0
        elif stat_type == "rushing":
            condition = advanced_table["attempts"] > 0
        elif stat_type == "receiving":
            condition = advanced_table["targets"] > 0
        advanced_table = advanced_table[condition]

        print(advanced_table)

        self.tables[table_keys[stat_type]]["advanced"].append(advanced_table)


    def extract_fumble_stats(self, file_name=""):
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