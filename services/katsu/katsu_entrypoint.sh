#!/bin/sh

# This line is necessary in order to give the database that is in another Docker container
# enough time to finish initializing
sleep 5

# Enables CORS for the React Researcher Portal which runs on port 3004
sed -i 's~CORS_ALLOWED_ORIGINS\s=\s\[\]~CORS_ALLOWED_ORIGINS = ["http://0.0.0.0:3004", "http://127.0.0.1:3004", "http://localhost:3004"]~' /app/chord_metadata_service/chord_metadata_service/metadata/settings.py

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000