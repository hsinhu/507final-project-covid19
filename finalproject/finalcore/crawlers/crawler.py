#################################
##### Name: Xin Hu
##### Uniqname: hsinhu
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3
# from db import insert_state_Cases, insert_county_Cases
# from db import insert_country_Cases, insert_Projection
from .cache import make_url_request_using_cache
import datetime
import time
import re
from .utils import clean_data, all_US_state_name
from iso3166 import countries
import csv
from ..models import CountryCases, StateCases, CountyCases, StateProjection
import us
import addfips

COVID19API_URL = "https://covidapi.info/api/v1/global/latest"
NYTCOVID19_URL = "https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html"

DBNAME = 'covid19.db'
CSV_Name = 'Hospitalization_all_locs.csv'

def get_country_cases():
    print("Start to get county cases...")
    today=str(datetime.date.today())
    params = {'date': today}
    response, using_cache = make_url_request_using_cache(COVID19API_URL,\
         params, "covid19api")

    if using_cache and CountryCases.objects.exists():
        return

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
            defaults = {'Confirmed': Confirmed, 'Deaths': Deaths, \
                'Recovered': Recovered}
            new_country, created = CountryCases.objects.update_or_create(
                    Country_ID=country_id, Country_Name=country_name,
                    defaults = defaults,
                )
            # insert_country_Cases(country_id, country_name, Confirmed, Deaths, Recovered)
    print("Finish county cases...")
    return


def get_state_name1(state_listing_li_tr):
    state_name_tag = state_listing_li_tr.find('td', recursive=False)
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
    state_name_tag = state_listing_li_tr.find('td', recursive=False)
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
    response, using_cache = make_url_request_using_cache(NYTCOVID19_URL, params, "nyt")
    state_dict = {}
    soup = BeautifulSoup(response, "html.parser")

    state_listing_parent = soup.find('table')
    state_listing_lis = state_listing_parent.find_all('tbody', recursive=False)
    for state_listing_li in state_listing_lis:
        state_listing_li_tr = state_listing_li.find('tr', recursive=False)
        state_name_tag, state_name = get_state_name1(state_listing_li_tr)
        if not state_name:
            continue
        state_link_tag = state_name_tag.find('a', recursive=False)
        if state_link_tag:
            state_details_url = state_link_tag['href']
            state_dict[state_name] = state_details_url
    return state_dict


def get_state_cases():
    print("Start get state cases in US...")
    today=str(datetime.date.today())
    params = {'date': today}
    response, using_cache = make_url_request_using_cache(NYTCOVID19_URL,\
         params, "nyt")

    if using_cache and StateCases.objects.exists():
        return

    state_dict = {}
    soup = BeautifulSoup(response, "html.parser")
    state_listing_parent = soup.find('table')
    state_listing_lis = state_listing_parent.find_all('tbody', recursive=False)

    for state_listing_li in state_listing_lis:
        state_listing_li_tr = state_listing_li.find('tr', recursive=False)
        _, state_name = get_state_name2(state_listing_li_tr)
        data = state_listing_li_tr.find_all('td', recursive=False)
        case_num = clean_data(data[1])
        case_per_100000_people = clean_data(data[2])
        death_num = clean_data(data[3])
        death_per_100000_people = clean_data(data[4])
        state = us.states.lookup(state_name)
        if state:
            fips = state.fips
            abbr = state.abbr
        else:
            if state_name == "U.S. Virgin Islands":
                fips = 78
                abbr = "VI"
            elif state_name == "Washington, D.C.":
                fips = 11
                abbr = "DC"

        defaults = {'Confirmed': case_num,
                    'State_fips': fips,
                    'State_abbr': abbr,
                    'Deaths': death_num,
                    'Confirmed_Per_100000_People': case_per_100000_people,
                    'Deaths_Per_100000_People': death_per_100000_people
                    }
        new_state, created = StateCases.objects.update_or_create(
                State_Name=state_name, defaults = defaults
            )
    print("Finish get state cases in US...")
    return


def get_county_cases_in_one_state(state_url, state_name, params):
    print("Start county in " + state_name + "...")
    response, using_cache = make_url_request_using_cache(state_url, params,\
         "nyt-county")

    if using_cache and CountyCases.objects.filter(stateCases__State_Name=state_name):
        return

    soup = BeautifulSoup(response, "html.parser")
    county_listing_parent = soup.find('tbody', class_='top-level')
    county_listing_lis = county_listing_parent.find_all('tr', recursive=False)
    af = addfips.AddFIPS()
    for county_listing_li in county_listing_lis[1:]:
        data = county_listing_li.find_all('td', recursive=False)
        county_name = clean_data(data[0])
        case_num = clean_data(data[1])
        case_per_100000_people = clean_data(data[2])
        death_num = clean_data(data[3])
        death_per_100000_people = clean_data(data[4])
        fips = None
        if county_name == 'New York City':
            fips = af.get_county_fips('New York County', state=state_name)
        elif county_name == 'LaSalle' and state_name == 'Louisiana':
            fips = af.get_county_fips('La Salle Parish', state=state_name)
        else:
            fips = af.get_county_fips(county_name, state=state_name)

            print(state_name, county_name)
        defaults = {'Confirmed': case_num,
                    'Deaths': death_num,
                    'Confirmed_Per_100000_People': case_per_100000_people,
                    'Deaths_Per_100000_People': death_per_100000_people}
        state = StateCases.objects.filter(State_Name=state_name).first()
        if not state:
            get_state_cases()
            state = StateCases.objects.filter(State_Name=state_name).first()
        new_county, created = CountyCases.objects.update_or_create(
                State_Name=state, County_name = county_name,
                County_fips = fips, defaults = defaults
            )
    print("Finish county in " + state_name + "...")
    return

def get_all_county_cases():
    today=str(datetime.date.today())
    params = {'date': today}

    state_dict = build_state_url_dict()
    today=str(datetime.date.today())
    params = {'date': today}
    response, using_cache = make_url_request_using_cache(NYTCOVID19_URL,\
         params, "nyt")

    for key in state_dict:
        state_url = state_dict[key]
        get_county_cases_in_one_state(state_url, key, params)
    return


def get_projection():
    if StateProjection.objects.exists():
        return
    file_contents = open(CSV_Name, 'r')
    if file_contents:
        print("can read")
    csv_reader = csv.reader(file_contents)
    next(csv_reader)
    for row in csv_reader:
        State_Name = row[1]
        # print(all_US_state_name)
        print(State_Name)
        if State_Name not in all_US_state_name:
            continue
        date_reported = row[3]
        allbed_mean = row[4]
        ICUbed_mean = row[7]
        InvVen_mean = row[10]
        deaths_mean_daily = row[13]
        totalDeath_mean = row[22]
        bedshortage_mean = row[25]
        icushortage_mean = row[28]

        defaults = {'allbed_mean': allbed_mean,
            'ICUbed_mean': ICUbed_mean,
            'InvVen_mean': ICUbed_mean,
            'deaths_mean_daily': deaths_mean_daily,
            'totalDeath_mean': totalDeath_mean,
            'bedshortage_mean': bedshortage_mean,
            'icushortage_mean': icushortage_mean}
        new_projection, created = StateProjection.objects.update_or_create(
                State_Name=State_Name, date_reported = date_reported,\
                     defaults = defaults
            )

    return

if __name__ == "__main__":
    print(build_state_url_dict())
    # print(len(build_state_url_dict()))

    # get_country_cases()
    # print()
    # get_state_cases()
    # print()
    # get_all_county_cases()

    # get_projection(CSV_Name)

