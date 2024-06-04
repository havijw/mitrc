"""
Methods for fetching Head of the Charles results from RegattaCentral.
"""

from functools import cache
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from analysis import get_times
from bs4 import BeautifulSoup

RC_YEARS = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023]

REGATTA_IDS = {
    2024: 8995,
    2023: 8392,
    2022: 6144,
    2021: 6143,
    2019: 6141,
    2018: 5656,
    2017: 4977,
    2016: 4699,
    2015: 4215,
    2014: 3644,
    2013: 3016,
    2012: 2327,
}

RC_RESULTS_PAGE = "https://www.regattacentral.com/regatta/results2"
RC_RESULTS_JSON = "https://www.regattacentral.com/servlet/DisplayRacesResults"
RC_RESULTS_PARAMS = {"Method": "getResults"}


@cache
def fetch_results_page(year: int) -> requests.Response:
    year_params = {"job_id": REGATTA_IDS[year]}
    return requests.get(f"{RC_RESULTS_PAGE}?{urlencode(year_params)}").text


def fetch_results(year: int, event: str) -> list[float]:
    # Fetch results page html in order to find event id
    results_page = fetch_results_page(year)
    results_soup = BeautifulSoup(results_page, features="html.parser")
    event_id = parse_qs(
        urlparse(results_soup.find("a", string=event).get("href")).query
    )["event_id"][0]
    # Fetch event results as json
    event_params = RC_RESULTS_PARAMS | {
        "job_id": REGATTA_IDS[year],
        "event_id": event_id,
    }
    results = (
        requests.get(f"{RC_RESULTS_JSON}?{urlencode(event_params)}")
        .json()
        .get("races")[0]
        .get("results")
    )
    return get_times(results)
