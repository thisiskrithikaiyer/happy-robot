from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Load(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_id = db.Column(db.String(50), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    pickup_datetime = db.Column(db.DateTime, nullable=False)
    delivery_datetime = db.Column(db.DateTime, nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    loadboard_rate = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    weight = db.Column(db.Float)
    commodity_type = db.Column(db.String(50))
    num_of_pieces = db.Column(db.Integer)
    miles = db.Column(db.Float)
    dimensions = db.Column(db.String(100))

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_id = db.Column(db.String(50), nullable=False)
    carrier_mc = db.Column(db.String(20), nullable=False)
    negotiated_price = db.Column(db.Float, nullable=True)
    outcome = db.Column(db.String(20), nullable=False)  # agreed, not_agreed
    sentiment = db.Column(db.String(20), nullable=False)  # positive, negative, neutral
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)