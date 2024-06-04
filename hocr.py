"""
Find and plot historical results for an event at the Head of the Charles Regatta.

Considers results since 2012, the first year results were posted to RegattaCentral.
"""

import math
from urllib.parse import parse_qs, urlencode, urlparse

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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


class Time(float):
    def __new__(cls, t):
        if isinstance(t, float):
            return float.__new__(cls, t)
        try:
            mins, secs = t.split(":")
            mins = int(mins)
            secs = float(secs)
            return float.__new__(cls, 60 * mins + secs)
        except ValueError:
            return float.__new__(cls, "nan")

    def __init__(self, time_str: str):
        super().__init__()

    def __repr__(self):
        if math.isnan(self):
            return ""
        mins = self.mins
        secs = self.secs
        return f"{mins}:{secs:06.3f}"

    @property
    def mins(self) -> int:
        return int(self / 60)

    @property
    def secs(self) -> float:
        return float(self % 60)

    def __add__(self, other: float):
        return Time(float(self) + other)

    def __sub__(self, other: float):
        return Time(float(self) - other)

    def __mul__(self, other: float):
        return Time(float(self) * other)

    def __truediv__(self, other: float):
        return Time(float(self) / other)

    def __floordiv__(self, other: float):
        return Time(float(self) // other)


def get_times(results: list[dict]) -> list[float]:
    """
    Get a list of adjusted finishing times, in finishing order.

    Params
    ------
    results: list[dict]
        Each element should have the following keys and value types:
            - finishPlace: int
            - adjustedTimeString: str

    Returns
    -------
    time: list[float]
        A list of adjusted finishing times, in seconds. List order is finishing
        order.
    """
    sorted_results = sorted(results, key=lambda r: r["finishPlace"])
    return [Time(result["adjustedTimeString"]) for result in sorted_results]


def get_winner(times: list[float]) -> float:
    """
    Find winning time among results.

    Params
    ------
    times: list[float]
        List of times, in seconds, in finishing order

    Returns
    -------
    winning_time: float
        Winning time
    """
    return times[0]


def get_percentile(times: list[float], percentile: float) -> float:
    """
    Find the time required to be in the top given percentile of the results.

    Params
    ------
    times: list[float]
        List of times, in seconds, in finishing order
    percentile: float
        Number X with 0 <= X <= 1 to find results in the top X percentile

    Returns
    -------
    percentile_time: float
        Slowest time among results in the top X percentile
    """
    percentile_num_entries = math.floor(percentile * len(times))
    return times[percentile_num_entries - 1]


if __name__ == "__main__":
    all_results = []
    for year in tqdm(RC_YEARS, desc="Loading results from RegattaCentral", unit="year"):
        year_params = {"job_id": REGATTA_IDS[year]}
        # Get event id
        results_page = requests.get(f"{RC_RESULTS_PAGE}?{urlencode(year_params)}")
        results_soup = BeautifulSoup(results_page.text, features="html.parser")
        event_id = parse_qs(
            urlparse(
                results_soup.find("a", string="Men's Club Eights").get("href")
            ).query
        )["event_id"][0]
        # Get results as json
        event_params = RC_RESULTS_PARAMS | year_params | {"event_id": event_id}
        results = (
            requests.get(f"{RC_RESULTS_JSON}?{urlencode(event_params)}")
            .json()
            .get("races")[0]
            .get("results")
        )
        all_results.append(get_times(results))
    winners = [get_winner(times) for times in all_results]
    tenth_percentile = [get_percentile(times, 0.1) for times in all_results]
    fiftieth_percentile = [get_percentile(times, 0.5) for times in all_results]

    fig, ax = plt.subplots()
    ax.plot(RC_YEARS, fiftieth_percentile, label="50th percentile")
    ax.plot(RC_YEARS, tenth_percentile, label="10th percentile")
    ax.plot(RC_YEARS, winners, label="Winner")
    ax.set(
        xlabel="Year", ylabel="Adjusted Finish Time", title="Men's Club Eight at HOCR"
    )
    ax.yaxis.set_major_formatter(
        lambda val, pos: f"{Time(val).mins}:{int(Time(val).secs):02d}"
    )
    ax.legend()
    plt.show()
