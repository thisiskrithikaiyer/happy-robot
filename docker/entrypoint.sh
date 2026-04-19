#!/bin/sh
set -e

python -c "
from app import app, db
from models import Load
with app.app_context():
    db.create_all()
    if Load.query.count() == 0:
        import create_sample_data
        create_sample_data.create_sample_loads()
        print('Sample data seeded')
    else:
        print('Data already exists, skipping seed')
"

exec gunicorn -b 0.0.0.0:8080 app:app
