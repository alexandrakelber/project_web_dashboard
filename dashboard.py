import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import os
import pytz
from datetime import datetime

def convert_to_local_time(timestamp, city):
    timezones = {
        "London": "Europe/London",
        "Paris": "Europe/Paris",
        "New York": "America/New_York"
    }

    tz = pytz.timezone(timezones.get(city, "UTC"))

    # Check if timestamp is already a datetime object, if it's an integer (Unix timestamp), convert it to datetime
    if isinstance(timestamp, int):
        timestamp = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

    # Convert timestamp to local time zone
    local_time = timestamp.astimezone(tz)

    return local_time.strftime("%Y-%m-%d %H:%M:%S")

# Check if the CSV is being read correctly
try:
    data = pd.read_csv('weather_data.txt')
    print("Data loaded successfully:")
    print(data.head())  # Print the first 5 rows to inspect the data
except Exception as e:
    print(f"Error loading file: {e}")

# --- Fonctions de chargement des données ---
def load_data(city="London"):
    DATA_FILE = 'weather_data.txt'
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()  # Fichier non trouvé => DataFrame vide
    try:
        data = pd.read_csv(DATA_FILE, parse_dates=['timestamp'])
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return pd.DataFrame()
    # Filtrer sur la ville demandée
    return data[data["city"] == city]

def load_daily_report(city="London"):
    # Remplacer les espaces par des underscores pour le nom du fichier
    city_underscore = city.replace(" ", "_")
    REPORT_FILE = f"daily_report_{city_underscore}.txt"
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, 'r') as file:
            return file.read()
    else:
        return f"Aucun rapport quotidien disponible pour {city}."

# --- Fonction de création du graphique ---
def create_figure(city="London"):
    data = load_data(city)
    if data.empty:
        fig = px.line(title=f'Aucune donnée disponible pour {city}')
    else:
        fig = px.line(
            data,
            x='timestamp',
            y='temp',
            title=f'Température au cours du temps pour {city}',
            markers=True  # Affiche un point pour chaque relevé
        )
        # Personnalisation des axes et du layout
        fig.update_xaxes(title='Horodatage', tickformat='%H:%M\n%d-%m')
        fig.update_yaxes(title='Température (°C)')
        fig.update_layout(
            margin=dict(l=40, r=40, t=60, b=40),
            plot_bgcolor='#fafafa',
            paper_bgcolor='#fafafa'
        )
    return fig

# --- Création de l'application Dash ---
app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'])


app.layout = html.Div(
    style={'maxWidth': '800px', 'margin': '0 auto'},
    children=[
        # Header
        html.Div(
            children=[
                html.H1("Dashboard Météo", style={'fontSize': '36px', 'textAlign': 'center', 'fontWeight': 'bold'}),
                html.P("Alexandra Kelber & Linn Juge", style={'textAlign': 'center', 'fontSize': '1rem', 'color': '#2c3e50'}),
                html.P("IF3", style={'textAlign': 'center', 'fontSize': '1rem', 'color': '#2c3e50'})
            ],
            style={
                'padding': '20px', 
                'backgroundColor': '#f8f9fa', 
                'borderBottom': '1px solid #dcdcdc',
                'marginBottom': '40px'
            }
        ),

        # Sélecteur de ville
        html.Div(
            children=[
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[
                        {'label': 'London', 'value': 'London'},
                        {'label': 'New York', 'value': 'New York'},
                        {'label': 'Paris', 'value': 'Paris'},
                    ],
                    value='London',
                    clearable=False,
                    style={'fontSize': '28px', 'padding': '10px'}
                )
            ],
            style={
                'padding': '20px', 
                'backgroundColor': '#ffffff', 
                'borderRadius': '10px', 
                'marginBottom': '30px',
                'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)' 
            }
        ),

        # Weather Section (Temperature and Time side by side)
        html.Div(
            children=[
                html.H2(id='current-temperature', style={'fontSize': '2rem', 'color': 'blue', 'marginBottom': '10px'}),
                html.P(id='current-time', style={'fontSize': '1.5rem', 'color': '#888'})
            ],
            style={'textAlign': 'center', 'marginBottom': '40px'}
        ),


        # Rest of the information in styled cards
        html.Div(
            children=[
                html.Div(
                    children=[html.P(id="current-feels-like", style={'fontSize': '18px', 'color': '#2c3e50'})],
                    style={'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}
                ),
                html.Div(
                    children=[html.P(id="current-humidity", style={'fontSize': '18px', 'color': '#2c3e50'})],
                    style={'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}
                ),
                html.Div(
                    children=[html.P(id="current-pressure", style={'fontSize': '18px', 'color': '#2c3e50'})],
                    style={'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}
                ),
                html.Div(
                    children=[html.P(id="current-wind-speed", style={'fontSize': '18px', 'color': '#2c3e50'})],
                    style={'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}
                ),
                html.Div(
                    children=[html.P(id="current-weather-desc", style={'fontSize': '18px', 'color': '#2c3e50'})],
                    style={'padding': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}
                ),
            ],
            style={'padding': '20px'}
        ),

        # Spinner pendant le chargement
        dcc.Loading(
            id="loading-data",
            type="default",
            children=html.Div(id="data-display", style={'margin': '20px 0'})
        ),

        # Graphique de la température
        html.Div(
            children=[
                dcc.Graph(id='temp-graph')
            ],
            style={
                'backgroundColor': '#ffffff',
                'borderRadius': '10px',
                'padding': '20px',
                'marginBottom': '30px'
            }
        ),

        # Affichage du rapport quotidien
        html.Div(
            children=[
                html.H3("Rapport Quotidien", style={'fontSize': '28px', 'fontWeight': 'bold', 'fontFamily': 'Georgia, serif'}),
                html.Div(id='daily-report')
            ],
            style={
                'backgroundColor': '#ffffff', 
                'borderRadius': '10px', 
                'padding': '20px',
                'marginBottom': '30px',
                'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)' 
            }
        ),

        # Interval de rafraîchissement (toutes les 5 minutes)
        dcc.Interval(
            id='interval-component',
            interval=5*60*1000,  # Rafraîchissement toutes les 5 minutes
            n_intervals=0
        )
    ]
)

@app.callback(
    [Output('current-temperature', 'children'),
     Output('current-time', 'children'),
     Output('current-feels-like', 'children'),
     Output('current-humidity', 'children'),
     Output('current-pressure', 'children'),
     Output('current-wind-speed', 'children'),
     Output('current-weather-desc', 'children')],
    [Input('city-dropdown', 'value')]
)
def update_weather(city):
    data = load_data(city)  # Ensure load_data fetches the correct data

    if data.empty:
        return ['Data not available'] * 7  # Provide fallback data if empty

    latest = data.iloc[-1]  # Get the latest weather data
    latest['timestamp'] = convert_to_local_time(latest['timestamp'], city)

    current_temp = f"{latest['temp']} °C"
    current_time = f"{latest['timestamp']}"
    current_feels_like = f"🌡️ Ressenti: {latest['feels_like']} °C"
    current_humidity = f"💧 Humidité: {latest['humidity']} %"
    current_pressure = f"⚖️ Pression: {latest['pressure']} hPa"
    current_wind_speed = f"🌬️ Vitesse du vent: {latest['wind_speed']} m/s"
    current_weather_desc = f"🌦️ Météo: {latest['weather_desc']}"

    return current_temp, current_time, current_feels_like, current_humidity, current_pressure, current_wind_speed, current_weather_desc

# --- Callback pour mettre à jour le dashboard ---
@app.callback(
    [Output('temp-graph', 'figure'),
     Output('daily-report', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('city-dropdown', 'value')]
)
def update_dashboard(n_intervals, city):
    data = load_data(city)

    if data.empty:
        info = html.P("Aucune donnée disponible pour le moment.", style={'color': 'red'})
        fig = create_figure(city)
    else:
        latest = data.iloc[-1]
        # Convert timestamp to local time
        latest['timestamp'] = convert_to_local_time(latest['timestamp'], city)

        # Create the weather info

        fig = create_figure(city)

    daily_report = load_daily_report(city)

    return fig, html.Pre(daily_report)

if __name__ == '__main__':
    print("Lancement du serveur Dash...")
    app.run(debug=True, host='0.0.0.0', port=8056)

