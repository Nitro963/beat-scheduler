#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py reset_db --noinput
python manage.py makemigrations
python manage.py migrate

# Load data
echo "Loading data"
python manage.py loaddata initial_data

echo "Seeding database"
python manage.py seed -t user_profile -n 50 -s 44

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000