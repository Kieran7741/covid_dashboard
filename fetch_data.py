import requests
import pprint
import time
import pandas as pd

status = ['confirmed', 'deaths', 'recovered']

covid_api ="https://api.covid19api.com/total/country/{country}"


def fetch_data_for_country(country):
    """
    Fetch totals for each day for the provided country
    :param country:
    :return:
    """
    print(f'Fetching data for {country}')
    url = covid_api.format(country=country)
    request = requests.get(url)
    return request.json()


def save_country_data_to_csv(data, file_name):
    """
    Convert the provided data to a csv
    :param data:
    :return:
    """
    data_frame = pd.DataFrame(data=data, columns=['Country', 'Date', 'Confirmed', 'Deaths', 'Recovered'])
    # update date string
    data_frame['Date'] = data_frame['Date'].apply(lambda date: date.split('T')[0])
    data_frame.to_csv(file_name)


if __name__ == '__main__':
    # Countries that border Germany
    countries = ['Germany', 'France', 'Netherlands', 'Switzerland', 'Austria',
                 'Czech Republic', 'Denmark', 'Poland','Luxembourg', 'Belgium']

    for country in countries:
        data = fetch_data_for_country(country)
        save_country_data_to_csv(data, f'data/{country}.csv')
        time.sleep(1)