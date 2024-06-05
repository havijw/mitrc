"""
Helper methods for analyzing Head of the Charles results.
"""

import math


class Time(float):
    """Simple class to format float quantities of seconds as mm:ss.xxx"""

    def __new__(cls, t):
        try:
            return float.__new__(cls, t)
        except ValueError:
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
            return "nan"
        return f"{self.mins}:{self.secs:06.3f}"

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


def get_top_fraction(times: list[float], fraction: float) -> float:
    """
    Get the slowest finishing time in the top `fraction` of results.

    Params
    ------
    times: list[float]
        List of times, in seconds, in finishing order
    fraction: float
        Desired cutoff for results to consider

    Returns
    -------
    percentile_time: float
        Slowest time among results in the top `fraction`
    """
    fraction_index = math.floor(fraction * (len(times) - 1))
    return times[fraction_index]
