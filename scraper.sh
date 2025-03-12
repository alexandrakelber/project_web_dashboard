#!/bin/bash 

# Variables
API_KEY="e3de4a3649f43d096433bbcd70d28644"
CITY=$1  # L'utilisateur peut maintenant passer le nom de la ville comme argument
URL="https://api.openweathermap.org/data/2.5/weather?q=${CITY// /%20}&appid=$API_KEY&units=metric"  # Remplace les espaces par %20

# Vérifier si curl est installé
command -v curl >/dev/null 2>&1 || { echo "curl est requis mais n'est pas installé. Arrêt du script."; exit 1; }

# Récupérer les données météo via curl
response=$(curl -s "$URL")

# Vérifier si la réponse contient une erreur
if [[ $(echo "$response" | jq -r '.cod') != "200" ]]; then
  echo "Erreur dans la récupération des données météo pour $CITY. Réponse : $response"
  exit 1
fi


echo "Données récupérées avec succès"

# Extraire les informations nécessaires avec jq
temp=$(echo $response | jq '.main.temp')
feels_like=$(echo $response | jq '.main.feels_like')
humidity=$(echo $response | jq '.main.humidity')
pressure=$(echo $response | jq '.main.pressure')
wind_speed=$(echo $response | jq '.wind.speed')
weather_desc=$(echo $response | jq -r '.weather[0].description')
temp_max=$(echo $response | jq '.main.temp_max')
temp_min=$(echo $response | jq '.main.temp_min')

# Vérifier si le fichier weather_data.txt existe, sinon le créer
if [ ! -f weather_data.txt ]; then
  echo "Le fichier weather_data.txt n'existe pas. Création du fichier."
  touch weather_data.txt
else
  echo "Le fichier weather_data.txt existe déjà."
fi

# Vider le fichier weather_data.txt avant d'écrire les nouvelles données
echo "Vider le fichier weather_data.txt avant d'ajouter les nouvelles données"
> weather_data.txt


# Stocker les informations dans un fichier texte
echo "$CITY, $temp, $feels_like, $humidity, $pressure, $wind_speed, $weather_desc, $temp_max, $temp_min" >> weather_data.txt
echo "Données ajoutées à weather_data.txt"

# Vérification des données avant d'écrire
echo "temp_max = $temp_max, temp_min = $temp_min"

# Ajouter la date et l'heure au fichier de données
echo "Job exécuté pour $CITY à : $(date)" >> weather_data.txt
echo "Date et heure ajoutées à weather_data.txt"

# Vérifier si le fichier daily_report.txt existe, sinon le créer
if [ ! -f daily_report.txt ]; then
  echo "Le fichier daily_report.txt n'existe pas. Création du fichier."
  touch daily_report.txt
else
  echo "Le fichier daily_report.txt existe déjà."
fi

# Vider le fichier daily_report.txt avant d'ajouter les nouvelles données
echo "Vider le fichier daily_report.txt avant d'ajouter les nouvelles données"
> daily_report.txt

# Calcul de l'humidité moyenne
avg_humidity=$(awk -F',' '{sum+=$3} END {print sum/NR}' weather_data.txt)


# Stocker ces informations dans un fichier de rapport
echo "Max Temp: $temp_max" >> daily_report.txt
echo "Min Temp: $temp_min" >> daily_report.txt
echo "Average Humidity: $avg_humidity%" >> daily_report.txt

#Message de confirmation
echo "Rapport quotidien créé dans daily_report.txt"
