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
app = dash.Dash(__name__)

app.layout = html.Div(
    style={'maxWidth': '800px', 'margin': '0 auto'},
    children=[
        html.H1("Dashboard Météo"),
       
        # Sélecteur de ville
        dcc.Dropdown(
            id='city-dropdown',
            options=[
                {'label': 'London', 'value': 'London'},
                {'label': 'New York', 'value': 'New York'},
                {'label': 'Paris', 'value': 'Paris'},
            ],
            value='London',
            clearable=False,
        ),
       
        # Spinner pendant le chargement
        dcc.Loading(
            id="loading-data",
            type="default",
            children=html.Div(id="data-display", style={'margin': '20px 0'})
        ),
       
        # Graphique de la température
        dcc.Graph(id='temp-graph'),
       
        # Affichage du rapport quotidien
        html.Div([
            html.H3("Rapport Quotidien"),
            html.Div(id='daily-report')
        ], style={'marginTop': '20px'}),
       
        # Interval de rafraîchissement (toutes les 5 minutes)
        dcc.Interval(
            id='interval-component',
            interval=5*60*1000,
            n_intervals=0
        )
    ]
)

# --- Callback pour mettre à jour le dashboard ---
@app.callback(
    [Output('data-display', 'children'),
     Output('temp-graph', 'figure'),
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
        latest = data.iloc[-1]  # Dernière ligne de données
        latest['timestamp'] = convert_to_local_time(latest['timestamp'], city)
        info = html.Div([
            html.P(f"Température: {latest['temp']} °C", style={'fontSize': '20px', 'color': 'blue'}),
            html.P(f"Ressenti: {latest['feels_like']} °C"),
            html.P(f"Humidité: {latest['humidity']} %"),
            html.P(f"Pression: {latest['pressure']} hPa"),
            html.P(f"Vitesse du vent: {latest['wind_speed']} m/s"),
            html.P(f"Météo: {latest['weather_desc']}"),
            html.P(f"Heure locale: {latest['timestamp']}")
        ])
        fig = create_figure(city)
   
    daily_report = load_daily_report(city)
   
    return info, fig, html.Pre(daily_report)

if __name__ == '__main__':
    print("Lancement du serveur Dash...")
    app.run(debug=True, host='0.0.0.0', port=8056)

