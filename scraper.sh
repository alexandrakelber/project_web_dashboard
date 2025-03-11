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
  echo "Le fichier weather_data.txt n'existe pas. Création du fichier."
  touch weather_data.txt
else
  echo "Le fichier weather_data.txt existe déjà."
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
echo "Le fichier weather_data.txt a été mis à jour."

# Ajouter la date et l'heure au fichier de données
echo "Job exécuté à : $(date)" >> weather_data.txt

# Calculer les statistiques du jour (exemples)
max_temp=$(awk -F',' '{if($1 > max_temp) max_temp=$1} END {print max_temp}' weather_data.txt)
min_temp=$(awk -F',' '{if($1 < min_temp) min_temp=$1} END {print min_temp}' weather_data.txt)
avg_humidity=$(awk -F',' '{sum+=$3} END {print sum/NR}' weather_data.txt)

# Stocker ces informations dans un fichier de rapport
echo "Max Temp: $max_temp" >> daily_report.txt
echo "Min Temp: $min_temp" >> daily_report.txt
echo "Average Humidity: $avg_humidity%" >> daily_report.txt

