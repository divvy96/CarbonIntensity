import datetime
import requests

import pandas

def get_current_intensity():
    response = requests.get(r'https://api.carbonintensity.org.uk/intensity')
    return response.json()['data'][0]['intensity']['actual']

def get_current_postcode_intensity(postcode: str):
    response = requests.get(f'https://api.carbonintensity.org.uk/regional/postcode/{postcode}')
    return response.json()['data'][0]['data'][0]['intensity']['forecast']

def get_forward_intensity(postcode: str, date_from: datetime.datetime):

    response = requests.get(f"https://api.carbonintensity.org.uk/regional/intensity/{date_from.isoformat()}/fw48h/postcode/{postcode}")
    json = response.json()

    data = {'from': [],
            'forecast': []}

    for record in json['data']['data']:
        data['from'].append(record['from'])
        data['forecast'].append(record['intensity']['forecast'])

    df = pandas.DataFrame(data)
    return df
