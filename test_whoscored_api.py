import pandas as pd
import time
import re
import json
pd.options.mode.chained_assignment = None
from bs4 import BeautifulSoup as soup
from collections import OrderedDict
try:
    from tqdm import trange
except ModuleNotFoundError:
    pass

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

main_url = 'https://1xbet.whoscored.com/'

def getLeagueUrls(minimize_window=True):

    #browser_options = ChromeOptions()
    browser_options = EdgeOptions()
    browser_options.add_argument("--headless=new")  # Nuova modalità headless più compatibile
    browser_options.add_argument("--disable-blink-features=AutomationControlled")  # Nasconde Selenium
    browser_options.add_argument("--window-size=1920x1080")  # Imposta una finestra visibile
    browser_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # Simula un utente reale
    browser_options.add_argument("--disable-gpu")  
    browser_options.add_argument("--no-sandbox")  
    browser_options.add_argument("--disable-dev-shm-usage")  
    browser_options.add_argument("--enable-unsafe-swiftshader")  

    #driver = webdriver.Chrome(options=browser_options)
    driver = webdriver.Edge(options=browser_options)

    # Nascondere il WebDriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    if minimize_window:
        driver.minimize_window()

    try:
        driver.get(main_url)
    except WebDriverException:
        driver.get(main_url)

    try:
        cookie_button = driver.find_element(By.XPATH, '//*[@id="qc-cmp2-container"]/div/div/div/div[2]/div/button[2]')
        driver.execute_script("arguments[0].click();", cookie_button)
    except NoSuchElementException:
        pass

    n_tournaments = []

    button_all_tournaments = driver.find_element(By.ID, "All-Tournaments-btn")
    driver.execute_script("arguments[0].click();", button_all_tournaments)

    alphabeth_buttons = driver.find_elements(By.XPATH, f'//*[contains(@id, "index-")]')
    for alphabeth_button in alphabeth_buttons:
        driver.execute_script("arguments[0].click();", alphabeth_button)
        countries = driver.find_elements(By.XPATH, f'//*[contains(@id, "tournamentNavButton-")]')

        for country in countries:
            driver.execute_script("arguments[0].click();", country)
            display_element = country.find_element(By.XPATH, 'following-sibling::*')
            tournaments_found_list = display_element.find_elements(By.XPATH, './/div[contains(@class, "TournamentsDropdownMenu-module_allTournamentNavButtons__")]')
            country_name = country.get_attribute('innerText')
            for tournament_found in tournaments_found_list:
                tournament_found_html = soup(tournament_found.get_attribute('innerHTML'), 'html.parser')
                n_tournaments.append({
                    'country': country_name,
                    'href': tournament_found_html.find('a').get('href'),
                    'name': tournament_found_html.find('a').get_text()
                })

    df_tournaments = pd.DataFrame(n_tournaments)
    df_tournaments.to_csv('tournaments.csv', index=False)

    driver.close()
    return df_tournaments

def getMatchData(url, minimize_window=True):

    #browser_options = ChromeOptions()
    browser_options = EdgeOptions()
    browser_options.add_argument("--headless=new")  # Nuova modalità headless più compatibile
    browser_options.add_argument("--disable-blink-features=AutomationControlled")  # Nasconde Selenium
    browser_options.add_argument("--window-size=1920x1080")  # Imposta una finestra visibile
    browser_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # Simula un utente reale
    browser_options.add_argument("--disable-gpu")  
    browser_options.add_argument("--no-sandbox")  
    browser_options.add_argument("--disable-dev-shm-usage")  
    browser_options.add_argument("--enable-unsafe-swiftshader")  

    #driver = webdriver.Chrome(options=browser_options)
    driver = webdriver.Edge(options=browser_options)

    # Nascondere il WebDriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    if minimize_window:
        driver.minimize_window()

    try:
        driver.get(url)
    except WebDriverException:
        driver.get(url)

    # get script data from page source
    script_content = driver.find_element(By.XPATH, '//*[@id="layout-wrapper"]/script[1]').get_attribute('innerHTML')


    # clean script content
    script_content = re.sub(r"[\n\t]*", "", script_content)
    script_content = script_content[script_content.index("matchId"):script_content.rindex("}")]


    # this will give script content in list form 
    script_content_list = list(filter(None, script_content.strip().split(',            ')))
    metadata = script_content_list.pop(1) 


    # string format to json format
    match_data = json.loads(metadata[metadata.index('{'):])
    keys = [item[:item.index(':')].strip() for item in script_content_list]
    values = [item[item.index(':')+1:].strip() for item in script_content_list]
    for key,val in zip(keys, values):
        match_data[key] = json.loads(val)


    # get other details about the match
    region = driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/span[1]').text
    league = driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/a').text.split(' - ')[0]
    season = driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/a').text.split(' - ')[1]
    if len(driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/a').text.split(' - ')) == 2:
        competition_type = 'League'
        competition_stage = ''
    elif len(driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/a').text.split(' - '))== 3:
        competition_type = 'Knock Out'
        competition_stage = driver.find_element(By.XPATH, '//*[@id="breadcrumb-nav"]/a').text.split(' - ')[-1]
    else:
        print('Getting more than 3 types of information about the competition.')

    match_data['region'] = region
    match_data['league'] = league
    match_data['season'] = season
    match_data['competitionType'] = competition_type
    match_data['competitionStage'] = competition_stage


    # sort match_data dictionary alphabetically
    match_data = OrderedDict(sorted(match_data.items()))
    match_data = dict(match_data)
    driver.close()
        
    return match_data

getLeagueUrls()