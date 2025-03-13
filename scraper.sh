#!/bin/bash
# scraper.sh - Récupère les données météo d'OpenWeatherMap et génère un rapport quotidien si demandé.
# Usage:
#   ./scraper.sh "City"           -> Récupère et ajoute une ligne de données pour la ville spécifiée
#   ./scraper.sh daily "City"     -> Même chose + génère le rapport quotidien pour la ville

# --- Détermination du mode ---
if [ "$1" == "daily" ]; then
    mode="daily"
    shift  # Supprime "daily" pour que $1 soit la ville
else
    mode="scrape"
fi

# --- Paramètres ---
CITY="${1:-London}"                         # Ville par défaut : London si non spécifiée
API_KEY="e3de4a3649f43d096433bbcd70d28644"    
BASE_URL="https://api.openweathermap.org/data/2.5/weather"
UNITS="metric"                              # Pour avoir les températures en °C

# Construction de l'URL (remplacement des espaces)
URL="${BASE_URL}?q=${CITY// /%20}&appid=${API_KEY}&units=${UNITS}"

# --- Récupération des données ---
response=$(curl -s "$URL")
if [ -z "$response" ]; then
    echo "Erreur: aucune réponse de OpenWeatherMap pour ${CITY}."
    exit 1
fi

# Extraction des champs avec grep -oP (regex Perl)
temp=$(echo "$response" | grep -oP '"temp":\s*\K[0-9.]+')
feels_like=$(echo "$response" | grep -oP '"feels_like":\s*\K[0-9.]+')
humidity=$(echo "$response" | grep -oP '"humidity":\s*\K[0-9.]+')
pressure=$(echo "$response" | grep -oP '"pressure":\s*\K[0-9.]+')
wind_speed=$(echo "$response" | grep -oP '"speed":\s*\K[0-9.]+')
weather_desc=$(echo "$response" | grep -oP '"description":\s*"\K[^"]+')
temp_max=$(echo "$response" | grep -oP '"temp_max":\s*\K[0-9.]+')
temp_min=$(echo "$response" | grep -oP '"temp_min":\s*\K[0-9.]+')

# Remplacement des champs vides par "N/A" si nécessaire
[ -z "$temp" ] && temp="N/A"
[ -z "$feels_like" ] && feels_like="N/A"
[ -z "$humidity" ] && humidity="N/A"
[ -z "$pressure" ] && pressure="N/A"
[ -z "$wind_speed" ] && wind_speed="N/A"
[ -z "$weather_desc" ] && weather_desc="N/A"
[ -z "$temp_max" ] && temp_max="N/A"
[ -z "$temp_min" ] && temp_min="N/A"

# Horodatage en format ISO (UTC)
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Stockage des données ---
DATA_FILE="weather_data.txt"
if [ ! -f "$DATA_FILE" ]; then
    echo "city,timestamp,temp,feels_like,humidity,pressure,wind_speed,weather_desc,temp_max,temp_min" > "$DATA_FILE"
fi

echo "${CITY},${timestamp},${temp},${feels_like},${humidity},${pressure},${wind_speed},${weather_desc},${temp_max},${temp_min}" >> "$DATA_FILE"
echo "Données ajoutées pour ${CITY} à ${timestamp}"

# --- Génération du rapport quotidien (si mode daily) ---
if [ "$mode" == "daily" ]; then
    # Remplacer les espaces dans CITY par des underscores (ex: "New York" -> "New_York")
    city_underscore="${CITY// /_}"
    REPORT_FILE="daily_report_${city_underscore}.txt"
    current_date=$(date -u +"%Y-%m-%d")
   
    # Filtrer les données du jour pour la ville spécifiée
    daily_data=$(awk -F',' -v date="$current_date" -v city="$CITY" '
        NR>1 && index($2, date)==1 && $1==city {print}
    ' "$DATA_FILE")
   
    if [ -z "$daily_data" ]; then
        echo "Aucune donnée pour le jour ${current_date} pour ${CITY}."
        exit 0
    fi

    open_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {print $3; exit}')
    close_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {val=$3} END{print (val=="")?"N/A":val}')
    min_temp=$(echo "$daily_data" | awk -F',' '$3 != "" { if(found==0 || $3 < min) {min=$3; found=1} } END{if(found==1) print min; else print "N/A"}')
    max_temp=$(echo "$daily_data" | awk -F',' '$3 != "" { if(found==0 || $3 > max) {max=$3; found=1} } END{if(found==1) print max; else print "N/A"}')
    avg_temp=$(echo "$daily_data" | awk -F',' '$3 != "" { sum+=$3; count++ } END{if(count>0) printf "%.2f", sum/count; else print "N/A"}')
    avg_humidity=$(echo "$daily_data" | awk -F',' '$5 != "" { sum+=$5; count++ } END{if(count>0) printf "%.2f", sum/count; else print "N/A"}')
   
    {
        echo "Rapport quotidien pour ${CITY} le ${current_date}:"
        echo "Température d'ouverture: ${open_temp} °C"
        echo "Température de clôture: ${close_temp} °C"
        echo "Température minimale: ${min_temp} °C"
        echo "Température maximale: ${max_temp} °C"
        echo "Température moyenne: ${avg_temp} °C"
        echo "Humidité moyenne: ${avg_humidity} %"
    } > "$REPORT_FILE"
   
    echo "Rapport quotidien généré dans ${REPORT_FILE}"
fi

