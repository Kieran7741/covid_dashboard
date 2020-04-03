
import requests
from requests.exceptions import HTTPError


def download_covid_dataset(file_name='covid_19_latest.csv',
                           url="https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"):
    try:
        req = requests.get(url=url)
        if req.ok:
            with open(file_name, 'wb') as covid:
                covid.write(req.content)
        else:
            raise HTTPError(req)
    except Exception as e:
        print(f'Failed to download dataset from {url} due to {e}')

download_covid_dataset()
