
# Line plot
import plotly.graph_objects as go
import numpy as np
import pandas as pd

countries = ['Germany', 'France', 'Netherlands', 'Switzerland',
             'Czechia', 'Denmark', 'Poland', 'Luxembourg', 'Belgium', 'Italy']


def generate_stats():
    """
    Generate basic stats DataFrame from covid 19 dataset
    :return: Statistics DataFrame
    """
    data = pd.read_csv('covid_19_latest.csv')
    stats_df = pd.DataFrame(columns=['country', 'total_cases', 'total_deaths', 'death_rate', 'geo_id'])
    for country in data.countriesAndTerritories.unique():
        country_df = data[data['countriesAndTerritories'] == country]
        country_population = country_df['popData2018'].unique()[0]
        total_cases = country_df.cases.sum()
        total_deaths = country_df.deaths.sum()
        death_rate = total_deaths/float(total_cases)
        stats_df = stats_df.append({'country': country, 'total_cases': total_cases, 'total_deaths': total_deaths,
                                    'death_rate': round(death_rate, 4), 'geo_id': country_df['countryterritoryCode'].unique()[0],
                                    'population': country_population}, ignore_index=True)

    return stats_df


def filter_by_country(country):
    """Retrieve data for a country"""
    loaded_data = pd.read_csv('covid_19_latest.csv')
    data = loaded_data[loaded_data.countriesAndTerritories == country]
    return data.iloc[::-1]


# Germany and surrounding countries
country_dfs = [filter_by_country(country) for country in countries]
germany_df = country_dfs[0]
germany_stats = go.Figure()
germany_stats.add_trace(go.Scatter(x=germany_df['dateRep'],
                                   y=germany_df['cases'], name='Cases',
                                   mode='lines+markers'))

germany_stats.add_trace(go.Scatter(x=germany_df['dateRep'],
                                   y=germany_df['deaths'], name='Deaths',
                                   mode='lines+markers'))

germany_stats.update_layout({'title': {'text': 'German Cases/Deaths', 'y': 0.95, 'x': 0.5,  'xanchor': 'center', 'yanchor': 'top'},
                             'xaxis_title': "Date", 'yaxis_title': "Cases"})


# Compare Germany to surrounding countries and standardise by population per million
cases_germany_surrounding = go.Figure()
deaths_germany_surrounding = go.Figure()
for name, country_df in zip(countries, country_dfs):
    cases_germany_surrounding.add_trace(go.Scatter(x=country_df['dateRep'], y=(country_df['cases'] / country_df['popData2018']) * 10 ** 6, name=name, mode='lines+markers'))
    deaths_germany_surrounding.add_trace(go.Scatter(x=country_df['dateRep'], y=(country_df['deaths'] / country_df['popData2018']) * 10 ** 6, name=name, mode='lines+markers'))

cases_germany_surrounding.update_layout({'title': {'text': 'Cases in and around Germany per population per million:', 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                                 'xaxis_title': "Date", 'yaxis_title': "Cases/million"})

deaths_germany_surrounding.update_layout({'title': {'text': 'Deaths in and around Germany per population per million:', 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                                 'xaxis_title': "Date", 'yaxis_title': "Deaths/million"})

world_stats = generate_stats()

global_case_death_rates = go.Figure(data=go.Choropleth(
    locations=world_stats['geo_id'],
    z=world_stats['death_rate'] * 100,
    colorscale='Reds',
    text=[f"{country} : {round(death_rate * 100, 3)}%" for country, death_rate in zip(world_stats['country'], world_stats['death_rate'])],
    hoverinfo='text'))
global_case_death_rates.update_layout(title='Global Case mortality rate(%)', title_x=0.5, title_y=0.95)


# Cases Pie chart

country_totals = [int(country['cases'].sum()) for country in country_dfs]

cases_pie = go.Figure(data=[go.Pie(labels=countries, values=country_totals, textinfo='label+value+percent',
                                   insidetextorientation='radial')])
cases_pie.update_layout({'title': {'text': 'Cases in and around Germany', 'y': 0.95, 'x': 0.5,  'xanchor': 'center', 'yanchor': 'top'}})


country_totals_per_million = [int((country['cases'].sum()/country['popData2018'].unique()[0]) * 10**6) for country in country_dfs]
country_cases_per_million = go.Figure(data=[go.Pie(labels=countries, values=country_totals_per_million, textinfo='label+value+percent',
                                                   insidetextorientation='radial')])
country_cases_per_million.update_layout({'title': {'text': 'Cases in and around Germany per population per million',
                                                   'y': 0.95, 'x': 0.5,  'xanchor': 'center', 'yanchor': 'top'}})


germany_stats.show()
cases_germany_surrounding.show()
deaths_germany_surrounding.show()
cases_pie.show()
country_cases_per_million.show()
global_case_death_rates.show()

