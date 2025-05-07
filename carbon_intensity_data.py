from collections import namedtuple

import datetime
import requests

import pandas

intensity = namedtuple("intensity", field_names=["carbon_intensity"], defaults=[None])


def get_historical_region_intensity(start_datetime: datetime.datetime, regionId: str):
    period_start = start_datetime.isoformat()
    url = f"https://api.carbonintensity.org.uk/regional/intensity/{period_start}/fw48h/regionid/{regionId}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retrieving data")
        return

    data = response.json()
    regional_intensity = []
    for start_time in data["data"]["data"]:
        regional_intensity.append(
            (
                data["data"]["regionid"],
                start_time["intensity"]["forecast"],
                start_time["from"],
                start_time["to"],
            )
        )
    df = pandas.DataFrame(
        regional_intensity, columns=["regionid", "forecast_intensity", "from", "to"]
    )
    return df


def get_historical_postcode_mix(start_datetime: datetime.datetime, postcode: str):
    period_start = start_datetime.isoformat()
    url = f"https://api.carbonintensity.org.uk/regional/intensity/{period_start}/fw48h/postcode/{postcode}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retreiving data")
        return

    data = response.json()
    generation_mix_history = []
    for start_time in data["data"]["data"]:
        for generation_values in start_time["generationmix"]:
            generation_mix_history.append(
                (
                    generation_values["fuel"],
                    generation_values["perc"],
                    start_time["from"],
                    start_time["to"],
                    postcode,
                )
            )

    df = pandas.DataFrame(
        generation_mix_history, columns=["fuel", "percentage", "from", "to", "postcode"]
    )
    df["from"] = pandas.to_datetime(df["from"])
    df["to"] = pandas.to_datetime(df["to"])
    return df


def get_current_intensity():
    """returns the current national g/CO2 equivalent emissions"""

    response = requests.get(r"https://api.carbonintensity.org.uk/intensity")
    if response.status_code == 200:
        return intensity(response.json()["data"][0]["intensity"]["actual"])
    else:
        return intensity()


def get_current_postcode_intensity(postcode: str):
    """returns the current g/CO2 equivalent emissions for the given postcode"""

    response = requests.get(
        f"https://api.carbonintensity.org.uk/regional/postcode/{postcode}"
    )
    if response.status_code == 200:
        return intensity(response.json()["data"][0]["data"][0]["intensity"]["forecast"])
    else:
        return intensity()


def get_forward_intensity(postcode: str, date_from: datetime.datetime):
    response = requests.get(
        f"https://api.carbonintensity.org.uk/regional/intensity/{date_from.isoformat()}/fw48h/postcode/{postcode}"
    )

    if response.status_code == 200 and response.text != "null":
        json = response.json()

        data = {"from": [], "forecast": []}

        for record in json["data"]["data"]:
            data["from"].append(record["from"])
            data["forecast"].append(record["intensity"]["forecast"])

        df = pandas.DataFrame(data)
        df["from"] = pandas.to_datetime(df["from"])
        return df
    else:
        return ""


def intensity_bands():
    # year = 2025
    # bandings are upadated periodically

    band_names = ["Very Low", "Low", "Moderate", "High", "Very High"]
    lower_bound = [0, 30, 100, 180, 250]
    upper_bound = [30, 100, 180, 250, 350]
    color = ["lightgreen", "green", "yellow", "coral", "red"]

    intensity_bands_df = pandas.DataFrame(
        {
            "intensity": band_names,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "color": color,
        }
    )
    return intensity_bands_df
