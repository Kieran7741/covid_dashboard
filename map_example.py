import plotly.express as px
import pandas as pd
import plotly.graph_objects as go



def generate_stats():
    """
    Generate basic stats DataFrame from covid 19 dataset
    :return: Statistics DataFrame
    """
    data = pd.read_csv('covid_19_latest.csv')
    stats = pd.DataFrame(columns=['country', 'total_cases', 'total_deaths', 'death_rate', 'geo_id'])
    for country in data.countriesAndTerritories.unique():
        country_df = data[data['countriesAndTerritories'] == country]
        total_cases = country_df.cases.sum()
        total_deaths = country_df.deaths.sum()
        deaths_per_population = total_deaths/float(total_cases)
        print(country_df['geoId'].unique()[0])
        stats = stats.append({'country': country, 'total_cases': total_cases, 'total_deaths': total_deaths,
                              'death_rate': round(deaths_per_population, 4), 'geo_id': country_df['countryterritoryCode'].unique()[0]}, ignore_index=True)

    return stats


df = generate_stats()

fig = go.Figure(data=go.Choropleth(

    locations=df['geo_id'], # Spatial coordinates
    z= df['total_deaths'], # Data to be color-coded
    colorscale='Blues',
    colorbar_title="Deaths",
))
fig.update_layout(title='Total Deaths')
fig.show()