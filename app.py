import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from requests import get
from requests.exceptions import HTTPError

# Helper functions #


def download_covid_dataset(file_name='covid_19_latest.csv',
                           url="https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"):
    """
    Download the latest covid 19 figures for each countries totals
    :param file_name: Save file name
    :param url: Remote dataset
    """

    try:
        req = get(url=url)
        if req.ok:
            with open(file_name, 'wb') as covid:
                covid.write(req.content)
        else:
            raise HTTPError(req)
    except Exception as e:
        print(f'Failed to download dataset from {url} due to {e}')


def generate_stats():
    """
    Generate basic stats DataFrame from covid 19 dataset
    :return: Statistics DataFrame
    """
    data = pd.read_csv('covid_19_latest.csv')
    stats_df = pd.DataFrame(columns=['country', 'total_cases', 'total_deaths', 'death_rate', 'geo_id'])
    for country in data.countriesAndTerritories.unique():
        country_df = data[data['countriesAndTerritories'] == country]
        total_cases = country_df.cases.sum()
        total_deaths = country_df.deaths.sum()
        deaths_per_population = total_deaths/float(total_cases)
        stats_df = stats_df.append({'country': country, 'total_cases': total_cases, 'total_deaths': total_deaths,
                              'death_rate': round(deaths_per_population, 4), 'geo_id': country_df['countryterritoryCode'].unique()[0]}, ignore_index=True)

    return stats_df


def filter_by_country(country):
    """Retrieve data for a country"""
    loaded_data = pd.read_csv('covid_19_latest.csv')
    data = loaded_data[loaded_data.countriesAndTerritories == country]
    return data

# Custom Dash components #


def drop_down_list(default):
    """
    Build drop down with all available countries
    """
    list_of_countries = sorted(list(set(pd.read_csv('covid_19_latest.csv')['countriesAndTerritories'])))

    return dcc.Dropdown(
        id='country_list',
        options=[{'label': country, 'value': country} for country in list_of_countries],
        value=default
    )


def graph_cases_deaths_for_country(country):
    data = filter_by_country(country)

    return html.Div(children=[
        html.H1(
            id='daily_total_header',
            children=f'Daily Figures: {country}',
            style={
                'textAlign': 'center',
                'color': 'black',
            }
        ),
        drop_down_list(country),
        dcc.Graph(id='cases_deaths_per_day',
                  figure={
                      'data': [{'x': list(reversed(list(data['dateRep'][:-50]))),
                                'y': list(reversed([int(count) for count in data['cases'][:-50]])), 'type': 'bar',
                                'name': 'Cases'},
                               {'x': list(reversed(list(data['dateRep'][:-50]))),
                                'y': list(reversed([int(count) for count in data['deaths'][:-50]])), 'type': 'bar',
                                'marker': {'color': 'red'}, 'name': 'Deaths'}
                               ],
                      'layout': {'xaxis': {'title': 'Date', 'tickangle': 45}, 'yaxis': {'title': 'Cases'}, 'title': 'Cases per day'}
                  },
                  )
    ])


def stats_table(stats_df):
    """
    Build stats table
    :param stats_df:
    :return:
    """

    return html.Div(style={'width': '75%', 'margin': 'auto', 'padding': '24px'},
                    children=[html.H2('Statistics Table:'),
                              dash_table.DataTable(
                                  id='stats_table',
                                  sort_action="native",
                                  columns=[{"name": i.upper(), "id": i} for i in stats_df.columns],
                                  data=stats_df.to_dict('records'),
                                  style_cell={'textAlign': 'left'})])


def world_map_deaths(stats_df):
    """
    World map displaying total deaths
    :param stats_df: Dataframe containing info to be plotted
    """
    fig = go.Figure(data=go.Choropleth(
        locations=stats_df['geo_id'],  # Spatial coordinates
        z=stats_df['total_deaths'],  # Data to be color-coded
        colorscale='Reds'
    ))
    fig.update_layout(title='Global Deaths', title_x=0.5, title_y=0.9)
    return html.Div(children=dcc.Graph(figure=fig, style={'height': '700px', 'width': '70%', 'margin': 'auto'}))


def world_map_death_rate(stats_df):
    """
    World map displaying total deaths
    :param stats_df: Dataframe containing info to be plotted
    """
    fig = go.Figure(data=go.Choropleth(
        locations=stats_df['geo_id'],  # Spatial coordinates
        z=stats_df['death_rate'],  # Data to be color-coded
        colorscale='Reds'
    ))
    fig.update_layout(title='Global_death_rates', title_x=0.5, title_y=0.9)
    return html.Div(children=dcc.Graph(figure=fig, style={'height': '700px', 'width': '70%', 'margin': 'auto'}))


def world_map_cases(stats_df):
    """
    World map displaying total deaths
    :param stats_df: Dataframe containing info to be plotted
    """
    fig = go.Figure(data=go.Choropleth(
        locations=stats_df['geo_id'],  # Spatial coordinates
        z=stats_df['total_cases'],  # Data to be color-coded
        colorscale='Blues'
    ))
    fig.update_layout(title='Global Cases', title_x=0.5, title_y=0.9)
    return html.Div(children=dcc.Graph(figure=fig, style={'height': '700px', 'width': '70%', 'margin': 'auto'}))


# Main Dashboard Creation#

download_covid_dataset()
stats = generate_stats()
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': 'white',
    'text': 'black'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    graph_cases_deaths_for_country('Germany'),
    world_map_cases(stats),
    world_map_deaths(stats),

    stats_table(stats)

])


@app.callback([Output('cases_deaths_per_day', 'figure'), Output('daily_total_header', 'children')],[Input('country_list', 'value')])
def update_daily_deaths_graph(country):
    data = filter_by_country(country)

    return [
        {
            'data': [{'x': list(reversed(list(data['dateRep'][:-50]))),
                      'y': list(reversed([int(count) for count in data['cases'][:-50]])), 'type': 'bar', 'name': 'Cases'},
                     {'x': list(reversed(list(data['dateRep'][:-50]))),
                      'y': list(reversed([int(count)for count in data['deaths'][:-50]])), 'type': 'bar',
                      'marker': {'color': 'red'}, 'name': 'Deaths'}
                     ],
            'layout': {'xaxis': {'title': 'Date', 'tickangle': 45}, 'yaxis': {'title': 'Cases'}, 'title': 'Cases/Deaths per day'}
        },
        f'Daily Figures: {country}']


if __name__ == '__main__':
    app.run_server(debug=True)
