import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Charger les données scrappées
def load_data():
    # Lire le fichier weather_data.txt pour afficher les dernières données
    data = pd.read_csv('weather_data.txt', header=None, names=["temp", "feels_like", "humidity", "pressure", "wind_speed", "weather_desc"])
    return data

# Créer l'application Dash
app = dash.Dash(__name__)

# Créer un graphique pour afficher la série temporelle des températures
def create_figure():
    data = load_data()
    fig = px.line(data, x=data.index, y='temp', title='Temperature over Time')
    return fig

# Définir la disposition du dashboard
app.layout = html.Div([
    html.H1("Weather Dashboard"),
    html.Div([
        html.P(id="temp-display"),
        html.P(id="feels-like-display"),
        html.P(id="humidity-display"),
        html.P(id="pressure-display"),
        html.P(id="wind-speed-display"),
        html.P(id="weather-display"),
    ]),
    dcc.Graph(id='temp-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # Interval de 5 minutes
        n_intervals=0
    )  # Ajout de l'interval pour rafraîchir toutes les 5 minutes
])

# Callback pour mettre à jour les éléments du dashboard
@app.callback(
    [Output('temp-display', 'children'),
     Output('feels-like-display', 'children'),
     Output('humidity-display', 'children'),
     Output('pressure-display', 'children'),
     Output('wind-speed-display', 'children'),
     Output('weather-display', 'children'),
     Output('temp-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    # Charger les données chaque fois que la fonction est appelée
    data = load_data()

    # Créer les éléments du dashboard
    temp = f"Temperature: {data['temp'].iloc[-1]} °C"
    feels_like = f"Feels Like: {data['feels_like'].iloc[-1]} °C"
    humidity = f"Humidity: {data['humidity'].iloc[-1]}%"
    pressure = f"Pressure: {data['pressure'].iloc[-1]} hPa"
    wind_speed = f"Wind Speed: {data['wind_speed'].iloc[-1]} m/s"
    weather_desc = f"Weather: {data['weather_desc'].iloc[-1]}"

    # Créer un graphique pour la température
    fig = create_figure()

    return temp, feels_like, humidity, pressure, wind_speed, weather_desc, fig

# Exécuter le serveur
if __name__ == '__main__':
    app.run_server(debug=True)


