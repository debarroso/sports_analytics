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
        self.parsed_path = str(self.current_path).replace("web_scraping", "datalake").replace("parsers", "parsed")
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
            "fumble_stats": {
                "basic": []
            },
            "defense_stats": {
                "basic": [],
                "advanced": []
            },
            "return_stats": {
                "basic": []
            },
            "kicking_stats": {
                "basic": []
            }
        }

    def parse(self):
        stat_types = [
            "passing",
            "rushing",
            "receiving",
            "fumbles",
            "defense",
            "returns",
            "kicking"
        ]

        for match_file in self.match_files:
            self.soup = self.get_soup(file_name=match_file)
            self.soup_str = str(self.soup)
            self.game_id = match_file.split(".")[0].split("\\")[-1]
            self.extract_game_details(file_name=match_file)
            self.extract_team_stats(file_name=match_file)
            for stat_type in stat_types:
                self.extract_numeric_stats(stat_type=stat_type, file_name=match_file)

    def get_files(self, file_name="*"):
        return glob.glob(f"{self.datalake_path}\\{file_name}")

    def get_soup(self, file_name=""):
        with open(file_name, mode="r", encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, features="lxml")
        return soup

    def clean_header(self, header=[]):
        return [c.replace(' ', '_').strip(".").lower() for c in header]

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

        game_info_dict = {}
        officials_dict = {}
        
        try:
            game_info = pd.read_html(self.soup_str, match="Game Info")
            game_info_keys = game_info[0]["Game Info"].values.tolist()
            game_info_values = game_info[0]["Game Info.1"].values.tolist()
            game_info_dict = dict(zip(self.clean_header(game_info_keys), game_info_values))

        except ValueError as e:
            
            if "No tables found" in str(e):
                print(f"no game info table found in {file_name}")

            else:
                raise
        
        try:
            officials = pd.read_html(self.soup_str, match="Officials")
            officials_keys = officials[0]["Officials"].values.tolist()
            officials_values = officials[0]["Officials.1"].values.tolist()
            officials_dict = dict(zip(self.clean_header(officials_keys), officials_values))

        except ValueError as e:
            
            if "No tables found" in str(e):
                print(f"no officials table found in {file_name}")

            else:
                raise

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

        team_stats = pd.read_html(self.soup_str, match="Team Stats")[0]
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

    def extract_numeric_stats(self, stat_type, file_name=""):
        game_id = self.game_id
        game_date = self.get_game_date(game_id=self.game_id)

        match_dict = {
            "passing": "Passing",
            "rushing": "Rushing",
            "receiving": "Receiving",
            "fumbles": "Passing, Rushing, & Receiving",
            "defense": "Defense",
            "returns": "Kick/Punt Returns",
            "kicking": "Kicking & Punting"
        }

        slice_dict = {
            "passing": [0,1,2,3,4,5,6,7,8,9,10],
            "rushing": [0,1,11,12,13,14],
            "receiving": [0,1,15,16,17,18,19],
            "fumbles": [0,1,20,21],
            "defense": [i for i in range(17)],
            "returns": [i for i in range(12)],
            "kicking": [i for i in range(10)]
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
            },
            "fumbles": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Fumbles_Fmb": "fumbles",
                "Fumbles_FL": "fumbles_lost"
            },
            "defense": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Def Interceptions_Int": "interceptions",
                "Def Interceptions_Yds": "interception_return_yards",
                "Def Interceptions_TD": "interceptions_returned_for_touchdown",
                "Def Interceptions_Lng": "longest_interception_return",
                "Def Interceptions_PD": "passes_defended",
                "Unnamed: 7_level_0_Sk": "sacks",
                "Tackles_Comb": "tackles_combined",
                "Tackles_Solo": "tackles_solo",
                "Tackles_Ast": "tackles_assisted",
                "Tackles_TFL": "tackles_for_loss",
                "Tackles_QBHits": "qb_hits",
                "Fumbles_FR": "fumbles_recovered",
                "Fumbles_Yds": "fumble_return_yards",
                "Fumbles_TD": "fumble_rec_touchdown",
                "Fumbles_FF": "forced_fumbles"
            },
            "returns": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Kick Returns_Rt": "kick_returns",
                "Kick Returns_Yds": "kick_return_yards",
                "Kick Returns_Y/Rt": "yards_per_kick_return",
                "Kick Returns_TD": "kick_return_touchdowns",
                "Kick Returns_Lng": "longest_kick_return",
                "Punt Returns_Ret": "punt_returns",
                "Punt Returns_Yds": "punt_return_yards",
                "Punt Returns_Y/R": "yards_per_punt_return",
                "Punt Returns_TD": "punt_return_touchdowns",
                "Punt Returns_Lng": "longest_punt_return"
            },
            "kicking": {
                "Unnamed: 0_level_0_Player": "player",
                "Unnamed: 1_level_0_Tm": "team",
                "Scoring_XPM": "extra_points_made",
                "Scoring_XPA": "extra_points_attempted",
                "Scoring_FGM": "field_goals_made",
                "Scoring_FGA": "field_goals_attempted",
                "Punting_Pnt": "punts",
                "Punting_Yds": "punt_yards",
                "Punting_Y/P": "yards_per_punt",
                "Punting_Lng": "longest_punt"
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
            },
            "defense": {
                "Player": "player",
                "Tm": "team",
                "Int": "interceptions",
                "Tgt": "targeted",
                "Cmp": "completions_when_targeted",
                "Cmp%": "completion_percentage_when_targeted",
                "Yds": "receiving_yards_allowed",
                "Yds/Cmp": "receiving_yards_allowed_per_completion",
                "Yds/Tgt": "yards_allowed_per_target",
                "TD": "receiving_touchdowns_allowed",
                "Rat": "pass_rating_when_targeted",
                "DADOT": "average_depth_of_target",
                "Air": "total_air_yards_on_completions",
                "YAC": "yards_after_catch_on_completions",
                "Bltz": "blitz",
                "Hrry": "qb_hurries",
                "QBKD": "qb_knockdowns",
                "Sk": "sacks",
                "Prss": "pressures",
                "Comb": "combined_tackles",
                "MTkl": "missed_tackles",
                "MTkl%": "missed_tackle_percentage"
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
            ],
            "fumbles": [
                "fumbles",
                "fumbles_lost"
            ],
            "defense": [
                "interceptions",
                "interception_return_yards",
                "interceptions_returned_for_touchdown",
                "longest_interception_return",
                "passes_defended",
                "sacks",
                "tackles_combined",
                "tackles_solo",
                "tackles_assisted",
                "tackles_for_loss",
                "qb_hits",
                "fumbles_recovered",
                "fumble_return_yards",
                "fumble_rec_touchdown",
                "forced_fumbles"
            ],
            "returns": [
                "kick_returns",
                "kick_return_yards",
                "yards_per_kick_return",
                "kick_return_touchdowns",
                "longest_kick_return",
                "punt_returns",
                "punt_return_yards",
                "yards_per_punt_return",
                "punt_return_touchdowns",
                "longest_punt_return"
            ],
            "kicking": [
                "extra_points_made",
                "extra_points_attempted",
                "field_goals_made",
                "field_goals_attempted",
                "punts",
                "punt_yards",
                "yards_per_punt",
                "longest_punt"
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
            ],
            "defense": [
                "interceptions",
                "targeted",
                "completions_when_targeted",
                "completion_percentage_when_targeted",
                "receiving_yards_allowed",
                "receiving_yards_allowed_per_completion",
                "yards_allowed_per_target",
                "receiving_touchdowns_allowed",
                "pass_rating_when_targeted",
                "average_depth_of_target",
                "total_air_yards_on_completions",
                "yards_after_catch_on_completions",
                "blitz",
                "qb_hurries",
                "qb_knockdowns",
                "sacks",
                "pressures",
                "combined_tackles",
                "missed_tackles",
                "missed_tackle_percentage"
            ]
        }

        table_keys = {
            "passing": "passing_stats",
            "rushing": "rushing_stats",
            "receiving": "receiving_stats",
            "fumbles": "fumble_stats",
            "defense": "defense_stats",
            "returns": "return_stats",
            "kicking": "kicking_stats"
        }

        try:
            tables = pd.read_html(self.soup_str, match=match_dict[stat_type], extract_links="body")

        except ValueError as e:
            
            if "No tables found" in str(e):
                print(f"{stat_type} table not found in {file_name}")
                return

            else:
                raise
        
        if stat_type == "defense":
            tables.pop(0)
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
        elif stat_type == "fumbles":
            condition = basic_table["fumbles"] > 0
        elif stat_type == "defense":
            condition = basic_table["interceptions"] >= 0
        elif stat_type == "returns":
            condition = basic_table["kick_returns"] >= 0
        elif stat_type == "kicking":
            condition = basic_table["punts"] >= 0
        basic_table = basic_table[condition]

        if not basic_table.empty:
            self.tables[table_keys[stat_type]]["basic"].append(basic_table)

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
        elif stat_type == "defense":
            condition = advanced_table["interceptions"] >= 0
        advanced_table = advanced_table[condition]

        if not advanced_table.empty:
            self.tables[table_keys[stat_type]]["advanced"].append(advanced_table)

    def save_parsed_data(self):
        for table in self.tables:
            
            if table in ["game_details", "team_stats"]:
                combined_df = pd.DataFrame(self.tables[table])
                combined_df.to_csv(f"{self.parsed_path}/{table}.csv", index=False, header=True)

            elif len(self.tables[table]) == 1:
                if len (self.tables[table]["basic"]) == 0:
                    break
                combined_df = pd.concat(self.tables[table]["basic"], ignore_index=True)
                combined_df.to_csv(f"{self.parsed_path}/{table}.csv", index=False, header=True)

            else:
                if len (self.tables[table]["basic"]) == 0:
                    break
                combined_df = pd.concat(self.tables[table]["basic"], ignore_index=True)
                combined_df.to_csv(f"{self.parsed_path}/{table}_basic.csv", index=False, header=True)

                if len (self.tables[table]["advanced"]) == 0:
                    break
                combined_df = pd.concat(self.tables[table]["advanced"], ignore_index=True)
                combined_df.to_csv(f"{self.parsed_path}/{table}_advanced.csv", index=False, header=True)


if __name__ == "__main__":
    parser = ProFootballRefParser()
    parser.parse()
    parser.save_parsed_data()