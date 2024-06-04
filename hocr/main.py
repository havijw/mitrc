"""
Find and plot historical results for an event at the Head of the Charles Regatta.

Considers results since 2012, the first year results were posted to RegattaCentral.
"""

import matplotlib.pyplot as plt
from analysis import Time, get_percentile
from results import RC_YEARS, fetch_results
from tqdm import tqdm


def plot_autoqualifying_times(
    results: dict[int, list[float]], event_name: str, ax: plt.Axes
):
    """
    Plot historical HOCR automatic qualifying times for an event.

    Params
    ------
    results: dict[int, list[float]]
        Dict giving the times for each year, in seconds, in finishing order
        Keys are the year of the results
    event_name: str
        Name of event
    ax: plt.Axes
        Axis on which to plot the automatic qualifying times
    """
    ax.plot(
        list(results.keys()),
        [get_percentile(times, 0.5) for times in results.values()],
        label=event_name,
    )


if __name__ == "__main__":
    events = {
        "Men's Eights": ["Men's Club Eights", "Men's Master Eights [40+]"],
        "Men's Fours": ["Men's Club Fours", "Men's Master Fours [40+]"],
        "Women's Eights": ["Women's Club Eights", "Women's Master Eights [40+]"],
        "Women's Fours": ["Women's Club Fours", "Women's Master Fours [40+]"],
    }
    results = {
        category: {
            event: {
                year: fetch_results(year, event)
                for year in tqdm(
                    RC_YEARS, desc=f"Fetching {event} results", unit="year"
                )
            }
            for event in events[category]
        }
        for category in events
    }

    fig, ((m8ax, w8ax), (m4ax, w4ax)) = plt.subplots(2, 2, figsize=(12.0, 6.0))
    for event_name, event_results in results["Men's Eights"].items():
        plot_autoqualifying_times(event_results, event_name, m8ax)
    for event_name, event_results in results["Men's Fours"].items():
        plot_autoqualifying_times(event_results, event_name, m4ax)
    for event_name, event_results in results["Women's Eights"].items():
        plot_autoqualifying_times(event_results, event_name, w8ax)
    for event_name, event_results in results["Women's Fours"].items():
        plot_autoqualifying_times(event_results, event_name, w4ax)
    for ax, category in zip(
        [m8ax, m4ax, w8ax, w4ax],
        ["Men's Eights", "Men's Fours", "Women's Eights", "Women's Fours"],
    ):
        ax.set(xlabel="Year", ylabel="Adjusted Finish Time", title=category)
        ax.yaxis.set_major_formatter(
            lambda val, pos: f"{Time(val).mins}:{int(Time(val).secs):02d}"
        )
        ax.legend(loc="lower left")
    fig.suptitle("HOCR Historical Automatic Qualifying Times")
    fig.tight_layout(w_pad=2.7, h_pad=1.62)
    plt.show()
