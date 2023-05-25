from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time, os


# competitions page https://fbref.com/en/comps/
# competition history https://fbref.com/en/comps/9/history/Premier-League-Seasons
# archived season https://fbref.com/en/comps/9/2021-2022/2021-2022-Premier-League-Stats
# competition fixtures https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures
# competition wages https://fbref.com/en/comps/9/wages/Premier-League-Wages

# example match date url https://fbref.com/en/matches/2023-04-22
# example player page https://fbref.com/en/players/e46012d4/Kevin-De-Bruyne
# example scouting report https://fbref.com/en/players/e46012d4/scout/365_m1/Kevin-De-Bruyne-Scouting-Report
# example team page https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats
# example match report https://fbref.com/en/matches/8358b4a1/Manchester-City-Real-Madrid-May-17-2023-Champions-League

driver = webdriver.Firefox()
firefox_options = Options()
# firefox_options.add_argument("--headless")
# firefox_options.add_argument("")
driver.get("")
