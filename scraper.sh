#!/bin/bash
# scraper.sh - Récupère les données météo et génère un rapport quotidien si demandé.

# --- Détermination du mode ---
if [ "$1" == "daily" ]; then
    mode="daily"
    shift  # Supprime "daily" des arguments pour que $1 soit ensuite le nom de la ville (optionnel)
else
    mode="scrape"
fi

# --- Paramètres ---
CITY="${1:-London}"                         # Utilise l'argument passé en ligne de commande ou "London" par défaut
API_KEY="e3de4a3649f43d096433bbcd70d28644"    # Clé API OpenWeatherMap
BASE_URL="https://api.openweathermap.org/data/2.5/weather"
UNITS="metric"                              # Pour avoir les températures en °C

# Construction de l'URL en encodant les espaces si besoin
URL="${BASE_URL}?q=${CITY// /%20}&appid=${API_KEY}&units=${UNITS}"

# --- Récupération des données ---
response=$(curl -s "$URL")
if [ -z "$response" ]; then
    echo "Erreur: aucune réponse de OpenWeatherMap."
    exit 1
fi

# Extraction des champs avec des regex Perl via grep -oP
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

# Création du fichier CSV avec en-tête s'il n'existe pas
if [ ! -f "$DATA_FILE" ]; then
    echo "city,timestamp,temp,feels_like,humidity,pressure,wind_speed,weather_desc,temp_max,temp_min" > "$DATA_FILE"
fi

# Ajout de la nouvelle ligne de données (format CSV)
echo "${CITY},${timestamp},${temp},${feels_like},${humidity},${pressure},${wind_speed},${weather_desc},${temp_max},${temp_min}" >> "$DATA_FILE"
echo "Données ajoutées pour ${CITY} à ${timestamp}"

# --- Génération du rapport quotidien (si mode daily) ---
if [ "$mode" == "daily" ]; then
    REPORT_FILE="daily_report.txt"
    current_date=$(date -u +"%Y-%m-%d")
    
    # Filtrer les données du jour pour la ville spécifiée
    daily_data=$(awk -F',' -v date="$current_date" -v city="$CITY" '
        NR>1 && index($2, date)==1 && $1==city {print}
    ' "$DATA_FILE")
    
    if [ -z "$daily_data" ]; then
        echo "Aucune donnée pour le jour ${current_date} pour ${CITY}."
        exit 0
    fi

    # Calcul des métriques (colonne 3 = temp)
    open_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {print $3; exit}')
    close_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {val=$3} END{print (val=="")?"N/A":val}')
    min_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {
        if(found==0 || $3 < min) {min=$3; found=1}
    } END{if(found==1) print min; else print "N/A"}')
    max_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {
        if(found==0 || $3 > max) {max=$3; found=1}
    } END{if(found==1) print max; else print "N/A"}')
    avg_temp=$(echo "$daily_data" | awk -F',' '$3 != "" {
        sum+=$3; count++
    } END{if(count>0) printf "%.2f", sum/count; else print "N/A"}')
    avg_humidity=$(echo "$daily_data" | awk -F',' '$5 != "" {
        sum+=$5; count++
    } END{if(count>0) printf "%.2f", sum/count; else print "N/A"}')
    
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
