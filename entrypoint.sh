#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "
import os, psycopg
conn = psycopg.connect(
    dbname=os.getenv('DB_NAME', 'ipsec_db'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'db'),
    port=os.getenv('DB_PORT', '5432'),
)
conn.close()
" 2>/dev/null; do
    echo "PostgreSQL not ready, retrying in 2s..."
    sleep 2
done
echo "PostgreSQL is ready!"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn ipsec_back.wsgi:application -c gunicorn.conf.py
