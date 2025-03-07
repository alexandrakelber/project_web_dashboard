#!/bin/bash

# Variables
API_KEY="e3de4a3649f43d096433bbcd70d28644"
CITY="London"
URL="https://api.openweathermap.org/data/2.5/weather?q=$CITY&appid=$API_KEY&units=metric"

# Vérifier si curl est installé
command -v curl >/dev/null 2>&1 || { echo "curl est requis mais n'est pas installé. Arrêt du script."; exit 1; }

# Récupérer les données météo via curl
response=$(curl -s "$URL")

# Vérifier si la réponse contient une erreur
if [[ $(echo "$response" | jq -r '.cod') != "200" ]]; then
  echo "Erreur dans la récupération des données météo. Réponse : $response"
  exit 1
fi

# Extraire les informations nécessaires avec jq
temp=$(echo $response | jq '.main.temp')
feels_like=$(echo $response | jq '.main.feels_like')
humidity=$(echo $response | jq '.main.humidity')
pressure=$(echo $response | jq '.main.pressure')
wind_speed=$(echo $response | jq '.wind.speed')
weather_desc=$(echo $response | jq -r '.weather[0].description')

# Vérifier si le fichier weather_data.txt existe, sinon le créer
if [ ! -f weather_data.txt ]; then
  touch weather_data.txt
fi

# Stocker les informations dans un fichier texte
echo "$temp, $feels_like, $humidity, $pressure, $wind_speed, $weather_desc" >> weather_data.txt

# Afficher les informations dans le terminal (optionnel)
echo "Temperature: $temp °C"
echo "Feels Like: $feels_like °C"
echo "Humidity: $humidity%"
echo "Pressure: $pressure hPa"
echo "Wind Speed: $wind_speed m/s"
echo "Weather Description: $weather_desc"
