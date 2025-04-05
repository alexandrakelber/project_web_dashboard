#!/bin/bash
echo "[INFO] $(date) - Starting update.sh" >> /home/ubuntu/update.log
cd /home/ubuntu/project_web_dashboard || { echo "[ERROR] Failed to cd" >> /home/ubuntu/update.log; exit 1; }
git pull origin main >> /home/ubuntu/update.log 2>&1
echo "[INFO] Finished git pull ✅" >> /home/ubuntu/update.log#!/bin/bash
cd /home/ubuntu/mon-scraper
git pull origin main
