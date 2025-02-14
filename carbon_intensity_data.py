import datetime
import requests

import pandas

def get_historical_postcode_mix(start_datetime: datetime.datetime, postcode: str):

    period_start = start_datetime.isoformat()
    url = f'https://api.carbonintensity.org.uk/regional/intensity/{period_start}/fw48h/postcode/{postcode}'
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retreiving data")
        return

    data = response.json()
    generation_mix_history = []
    for start_time in data['data']['data']:
        for generation_values in start_time['generationmix']:
            generation_mix_history.append(
                    (generation_values['fuel'],
                     generation_values['perc'],
                     start_time['from'],
                     start_time['to'],
                     postcode))

    df = pandas.DataFrame(generation_mix_history,
                          columns = ['fuel',
                                     'percentage',
                                     'from',
                                     'to'])
    df['from'] = pandas.to_datetime(df['from'])
    df['to'] = pandas.to_datetime(df['to'])
    return df

def get_current_intensity():
    response = requests.get(r"https://api.carbonintensity.org.uk/intensity")
    return response.json()["data"][0]["intensity"]["actual"]


def get_current_postcode_intensity(postcode: str):
    response = requests.get(
        f"https://api.carbonintensity.org.uk/regional/postcode/{postcode}"
    )
    if response.status_code == 200:
        return response.json()["data"][0]["data"][0]["intensity"]["forecast"]
    else:
        return ""


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
    band_names = ["Very Low", "Low", "Moderate", "High", "Very High"]
    carbon_limits = [0, 30, 100, 180, 250]
    return zip(carbon_limits, band_names)
