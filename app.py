import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from requests import get
from requests.exceptions import HTTPError
from dash.dependencies import Input, Output


def drop_down_list():
    """
    Build drop down with all available countries
    :return:
    """
    list_of_countries = sorted(list(set(pd.read_csv('covid_19_latest.csv')['countriesAndTerritories'])))

    return dcc.Dropdown(
        id='country_list',
        options=[{'label': country, 'value': country} for country in list_of_countries],
        value=list_of_countries[0]
    )


def filter_by_country(country):
    """Retrieve data for a country"""
    loaded_data = pd.read_csv('covid_19_latest.csv')
    data = loaded_data[loaded_data.countriesAndTerritories == country]
    return data


def graph_deaths_for_country(country):
    data = filter_by_country(country)

    return html.Div(children=[
        html.H1(
            id='daily_total_header',
            children=f'Daily Deaths: {country}',
            style={
                'textAlign': 'center',
                'color': 'white',
            }
        ),
        drop_down_list(),
        dcc.Graph(id='deaths_per_day',
                  figure={
                      'data': [{'x': list(reversed(list(data['dateRep']))),
                                'y': list(reversed([int(count) for count in data['deaths']])), 'type': 'bar',
                                'name': country}]
                  })
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    graph_deaths_for_country('Germany'),
])


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


def example_graph():
    df = pd.read_csv(
        'https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

    return html.Div([
        dcc.Graph(
            id='daily_deaths',
            figure={
                'data': [
                    dict(
                        x=df[df['continent'] == i]['gdp per capita'],
                        y=df[df['continent'] == i]['life expectancy'],
                        text=df[df['continent'] == i]['country'],
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}
                        },
                        name=i
                    ) for i in df.continent.unique()
                ],
                'layout': dict(
                    xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                    yaxis={'title': 'Life Expectancy'},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        )
    ])


@app.callback([Output('deaths_per_day', 'figure'), Output('daily_total_header', 'children')],
              [Input('country_list', 'value')])
def update_daily_deaths_graph(country):
    data = filter_by_country(country)

    return [{
        'data': [{'x': list(reversed(list(data['dateRep']))),
                  'y': list(reversed([int(count) for count in data['deaths']])), 'type': 'bar', 'name': country}]},
        f'Daily Deaths: {country}']


if __name__ == '__main__':
    print('Downloading latest Covid-19 figures.')
    download_covid_dataset()
    app.run_server(debug=True)
