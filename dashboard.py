import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Charger les données scrappées
data = pd.read_csv('weather_data.txt', header=None, names=["temp", "feels_like", "humidity", "pressure", "wind_speed", "weather_desc"])

# Créer l'application Dash
app = dash.Dash(__name__)

# Créer un graphique pour afficher la série temporelle des températures
fig = px.line(data, x=data.index, y='temp', title='Temperature over Time')

# Définir la disposition du dashboard
app.layout = html.Div([
    html.H1("Weather Dashboard"),
    html.Div([
        html.P(f"Temperature: {data['temp'].iloc[-1]} °C"),
        html.P(f"Feels Like: {data['feels_like'].iloc[-1]} °C"),
        html.P(f"Humidity: {data['humidity'].iloc[-1]}%"),
        html.P(f"Pressure: {data['pressure'].iloc[-1]} hPa"),
        html.P(f"Wind Speed: {data['wind_speed'].iloc[-1]} m/s"),
        html.P(f"Weather: {data['weather_desc'].iloc[-1]}"),
    ]),
    dcc.Graph(figure=fig)  # Ajouter le graphique
])

if __name__ == '__main__':
    app.run_server(debug=True)
