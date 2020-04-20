#################################
##### Name: Xin Hu
##### Uniqname: hsinhu
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import sqlite3
from db import insert_state_Cases, insert_county_Cases
from db import insert_country_Cases, insert_Projection
from cache import make_url_request_using_cache
import datetime
import time
import re
from utils import clean_data, all_US_state_name
from iso3166 import countries
import csv


COVID19API_URL = "https://covidapi.info/api/v1/global/latest"
NYTCOVID19_URL = "https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
CACHE_FILE_NAME = 'cache.json'
API_KEY = secrets.API_KEY
DBNAME = 'covid19.db'
CSV_Name = 'Hospitalization_all_locs.csv'

def get_country_cases():
    print("Start to get county cases...")
    today=str(datetime.date.today())
    params = {'date': today}
    response = make_url_request_using_cache(COVID19API_URL, params, "covid19api")
    results = response["result"]
    for result in results:
        for key in result:
            data = result[key]
            Confirmed = data["confirmed"]
            Deaths = data["deaths"]
            Recovered = data["recovered"]
            if key == 'MSZ' or key == "DPS":
                continue
            elif key == "WBG":
                country_id = key
                country_name = "West Bank & Gaza"
            else:
                if key == "RKS":
                    country_id = "XKX"
                else:
                    country_id = key
                country = countries.get(country_id)
                country_name = country.name
            insert_country_Cases(country_id, country_name, Confirmed, Deaths, Recovered)
    print("Finish county cases...")
    return


def get_state_name1(state_listing_li_tr):
    state_name_tag = state_listing_li_tr.find('td', class_=\
    'text svelte-5vyzvh', recursive=False)
    if not state_name_tag:
        state_name_tag = state_listing_li_tr.find('td', class_=\
        'text svelte-5vyzvh no-expand', recursive=False)
    state_name = state_name_tag.text.strip()
    name_list = re.split("[+|»]", state_name)
    clean_state_name = None
    for name in name_list:
        if name and "+" in state_name:
            clean_state_name = name.strip()
            if "MAP" in name:
                clean_state_name = clean_state_name[:-4]
    return state_name_tag, clean_state_name


def get_state_name2(state_listing_li_tr):
    state_name_tag = state_listing_li_tr.find('td', class_=\
    'text svelte-5vyzvh', recursive=False)
    if not state_name_tag:
        state_name_tag = state_listing_li_tr.find('td', class_=\
        'text svelte-5vyzvh no-expand', recursive=False)
    state_name = state_name_tag.text.strip()
    name_list = re.split("[+|»]", state_name)
    clean_state_name = None
    for name in name_list:
        if name:
            clean_state_name = name.strip()
            if "MAP" in name:
                clean_state_name = clean_state_name[:-4]
    return state_name_tag, clean_state_name


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url
    from New York Times

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
    '''
    today=str(datetime.date.today())
    params = {'date': today}
    response = make_url_request_using_cache(NYTCOVID19_URL, params, "nyt")
    state_dict = {}
    soup = BeautifulSoup(response, "html.parser")
    state_listing_parent = soup.find('table', class_=\
        'svelte-1d7u5bz')
    state_listing_lis = state_listing_parent.find_all('tbody', recursive=False)
    for state_listing_li in state_listing_lis:
        ## extract every state's URL
        state_listing_li_tr = state_listing_li.find('tr', class_=\
        'svelte-5vyzvh', recursive=False)
        state_name_tag, state_name = get_state_name1(state_listing_li_tr)
        if not state_name:
            continue
        state_link_tag = state_name_tag.find('a', class_=\
        'svelte-5vyzvh has-plus', recursive=False)
        if not state_link_tag:
            state_link_tag = state_name_tag.find('a', class_=\
            'svelte-5vyzvh', recursive=False)
        if state_link_tag:
            state_details_url = state_link_tag['href']
            state_dict[state_name] = state_details_url
    return state_dict


def get_state_cases():
    print("Start get state cases in US...")
    today=str(datetime.date.today())
    params = {'date': today}
    response = make_url_request_using_cache(NYTCOVID19_URL, params, "nyt")
    state_dict = {}
    soup = BeautifulSoup(response, "html.parser")
    state_listing_parent = soup.find('table', class_=\
        'svelte-1d7u5bz')
    state_listing_lis = state_listing_parent.find_all('tbody', recursive=False)

    for state_listing_li in state_listing_lis:
        state_listing_li_tr = state_listing_li.find('tr', class_=\
        'svelte-5vyzvh', recursive=False)
        _, state_name = get_state_name2(state_listing_li_tr)
        data = state_listing_li_tr.find_all('td', recursive=False)
        case_num = clean_data(data[1])
        case_per_100000_people = clean_data(data[2])
        death_num = clean_data(data[3])
        death_per_100000_people = clean_data(data[4])
        # print(state_name, case_num, case_per_100000_people,\
        #     death_num, death_per_100000_people)
        insert_state_Cases(state_name, case_num, case_per_100000_people,\
            death_num, death_per_100000_people)

    print("Finish get state cases in US...")
    return


def get_county_cases_in_one_state(state_url, state_name, params):
    print("Start county in " + state_name + "...")
    response = make_url_request_using_cache(state_url, params, "nyt-county")
    soup = BeautifulSoup(response, "html.parser")
    county_listing_parent = soup.find('tbody', class_='top-level')
    county_listing_lis = county_listing_parent.find_all('tr', recursive=False)

    for county_listing_li in county_listing_lis[1:]:
        data = county_listing_li.find_all('td', recursive=False)
        county_name = clean_data(data[0])
        case_num = clean_data(data[1])
        case_per_100000_people = clean_data(data[2])
        death_num = clean_data(data[3])
        death_per_100000_people = clean_data(data[4])
        # print(state_name, county_name, case_num, case_per_100000_people,\
        #     death_num, death_per_100000_people)
        insert_county_Cases(state_name, county_name, case_num, case_per_100000_people,\
            death_num, death_per_100000_people)
    print("Finish county in " + state_name + "...")
    return

def get_all_county_cases():
    today=str(datetime.date.today())
    params = {'date': today}
    state_dict = build_state_url_dict()
    today=str(datetime.date.today())
    params = {'date': today}

    for key in state_dict:
        state_url = state_dict[key]
        get_county_cases_in_one_state(state_url, key, params)
    return


def get_projection(CSV_Name):
    file_contents = open(CSV_Name, 'r')
    csv_reader = csv.reader(file_contents)
    next(csv_reader)
    for row in csv_reader:
        State_Name = row[1]
        if State_Name not in all_US_state_name:
            continue
        date_reported = row[2]
        allbed_mean = row[3]
        ICUbed_mean = row[6]
        InvVen_mean = row[9]
        deaths_mean_daily = row[12]
        totalDeath_mean = row[21]
        bedshortage_mean = row[24]
        icushortage_mean = row[27]
        insert_Projection(State_Name, date_reported, allbed_mean, \
            ICUbed_mean, InvVen_mean, deaths_mean_daily, totalDeath_mean,\
            bedshortage_mean, icushortage_mean)
    return

if __name__ == "__main__":
    # print(build_state_url_dict())
    # print(len(build_state_url_dict()))

    # get_country_cases()
    # print()
    # get_state_cases()
    # print()
    # get_all_county_cases()

    get_projection(CSV_Name)

