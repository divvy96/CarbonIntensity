from collections import namedtuple
import datetime

import requests

intensity = namedtuple("intensity", field_names=["carbon_intensity"], defaults=[None])

generation_mix = namedtuple(
    "generation_mix",
    field_names=["region_id", "fuel", "percentage", "start_time", "end_time"]
)

regional_temporal_intensity = namedtuple(
    "regional_temporal_intensity",
    field_names=["region_id", "intensity", "start_time", "end_time"],
)


def get_48hr_region_intensity(start_datetime: datetime.datetime, region_id: str):
    """returns the regional g/CO2 equivalent emissions for a specified region"""

    period_start = start_datetime.isoformat()
    url = f"https://api.carbonintensity.org.uk/regional/intensity/{period_start}/fw48h/regionid/{region_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retrieving data")
        return

    data = response.json()
    regional_intensity = []
    for start_time in data["data"]["data"]:
        regional_intensity_row = regional_temporal_intensity(
            region_id=data["data"]["regionid"],
            intensity=start_time["intensity"]["forecast"],
            start_time=start_time["from"],
            end_time=start_time["to"],
        )
        regional_intensity.append(regional_intensity_row)

    return regional_intensity


def get_48hr_postcode_intensity(start_datetime: datetime.datetime, postcode: str):
    """returns the regional g/CO2 equivalent emissions for specified region, using postcode to determine the region"""
 
    period_start = start_datetime.isoformat()

    url = f"https://api.carbonintensity.org.uk/regional/intensity/{period_start}/fw48h/postcode/{postcode}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retrieving data")

    data = response.json()

    regional_intensity = []
    for start_time in data["data"]["data"]:
        regional_intensity_row = regional_temporal_intensity(
            region_id=data["data"]["regionid"],
            intensity=start_time["intensity"]["forecast"],
            start_time=start_time["from"],
            end_time=start_time["to"],
        )
        regional_intensity.append(regional_intensity_row)

    return regional_intensity


def get_historical_postcode_mix(start_datetime: datetime.datetime, postcode: str):
    """get the percentage of each fuel used for a 48hour window for a particular postcode"""

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
            generation_mix_row = generation_mix(
                fuel=generation_values["fuel"],
                percentage=generation_values["perc"],
                start_time=start_time["from"],
                end_time=start_time["to"],
                region_id=data["data"]["regionid"]
            )
            generation_mix_history.append(generation_mix_row)

    return generation_mix_history


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


def intensity_bands():
    # year = 2025
    # bandings are upadated periodically

    band_names = ["Very Low", "Low", "Moderate", "High", "Very High"]
    lower_bound = [0, 30, 100, 180, 250]
    upper_bound = [30, 100, 180, 250, 350]
    color = ["lightgreen", "green", "yellow", "coral", "red"]

    intensity_bands = {
            "intensity": band_names,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "color": color,
        }
    return intensity_bands
