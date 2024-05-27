from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time, os, json, pathlib


current_path = pathlib.Path(__file__).parent.resolve()
driver = webdriver.Firefox()
firefox_options = Options()
# firefox_options.add_argument("--headless")
# firefox_options.add_argument("")


def get_leagues():
    with open(f"{current_path}/helpers/league_links.json") as fp:
        leagues = json.loads(fp.read())
    return leagues


def get_league_seasons(league):
    print(league)
    driver.get(f"{league['link']}")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "seasons")))
    seasons_table = driver.find_element_by_id("seasons")

    html = seasons_table.get_attribute("outHTML")

    print(html)


leagues = get_leagues()
get_league_seasons(league=leagues["Premier_League"])
