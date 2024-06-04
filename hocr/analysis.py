"""
Methods for analyzing Head of the Charles results.
"""

import math


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
