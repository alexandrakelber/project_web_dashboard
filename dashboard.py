import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Charger les données scrappées
def load_data(city="London"):
    data = pd.read_csv('weather_data.txt', header=None, names=["city", "temp", "feels_like", "humidity", "pressure", "wind_speed", "weather_desc", "temp_max", "temp_min"])
    return data[data["city"] == city]

# Charger le rapport quotidien
def load_daily_report():
    with open('daily_report.txt', 'r') as file:
        return file.readlines()

# Créer l'application Dash
app = dash.Dash(__name__)

# Créer un graphique pour afficher la série temporelle des températures
def create_figure(city="London"):
    data = load_data(city)
    fig = px.line(data, x=data.index, y='temp', title=f'Temperature over Time in {city}')
    return fig

# Définir la disposition du dashboard
app.layout = html.Div([
    html.H1("Weather Dashboard"),

    # Dropdown pour sélectionner la ville
    dcc.Dropdown(
        id='city-dropdown',
        options=[
            {'label': 'London', 'value': 'London'},
            {'label': 'New York', 'value': 'New York'},
            {'label': 'Paris', 'value': 'Paris'},
        ],
        value='London',
    ),

    # Affichage des données en temps réel
    html.Div([
        html.P(id="temp-display"),
        html.P(id="feels-like-display"),
        html.P(id="humidity-display"),
        html.P(id="pressure-display"),
        html.P(id="wind-speed-display"),
        html.P(id="weather-display"),
    ]),

    # Graphiques
    dcc.Graph(id='temp-graph'),

    # Affichage du rapport quotidien
    html.Div([
        html.H3("Daily Report"),
        html.Div(id='daily-report')
    ]),

    # Interval pour rafraîchir les données
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # Rafraîchissement toutes les 5 minutes
        n_intervals=0
    )
])

# Callback pour mettre à jour les éléments du dashboard
@app.callback(
    [Output('temp-display', 'children'),
     Output('feels-like-display', 'children'),
     Output('humidity-display', 'children'),
     Output('pressure-display', 'children'),
     Output('wind-speed-display', 'children'),
     Output('weather-display', 'children'),
     Output('temp-graph', 'figure'),
     Output('daily-report', 'children')],  # Ajouter le rapport quotidien à l'affichage
    [Input('interval-component', 'n_intervals'),
     Input('city-dropdown', 'value')]  # Nouvelle entrée pour la ville
)

def update_dashboard(n_intervals, city):
    # Charger les données chaque fois que la fonction est appelée
    data = load_data(city)

    # Créer les éléments du dashboard
    temp = f"Temperature: {data['temp'].iloc[-1]} °C"
    feels_like = f"Feels Like: {data['feels_like'].iloc[-1]} °C"
    humidity = f"Humidity: {data['humidity'].iloc[-1]}%"
    pressure = f"Pressure: {data['pressure'].iloc[-1]} hPa"
    wind_speed = f"Wind Speed: {data['wind_speed'].iloc[-1]} m/s"
    weather_desc = f"Weather: {data['weather_desc'].iloc[-1]}"

    # Créer un graphique pour la température
    fig = create_figure(city)

    # Charger le rapport quotidien
    report = load_daily_report()

    return temp, feels_like, humidity, pressure, wind_speed, weather_desc, fig, html.Div([html.P(line) for line in report])

# Exécuter le serveur
if __name__ == '__main__':
    print("Dash server is running...")
    app.run_server(debug=True, host='0.0.0.0', port=8052)
