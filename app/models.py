from . import db
from datetime import datetime

class FuelType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    base_price = db.Column(db.Float, default=0.0)
    
    # One FuelType has many DailyLogs and many Receipts
    # These 'backrefs' automatically create the .fuel_type attribute on the children
    daily_logs = db.relationship('DailyLog', backref='fuel_type', lazy=True)
    receipts = db.relationship('Receipt', backref='fuel_type', lazy=True)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fuel_id = db.Column(db.Integer, db.ForeignKey('fuel_type.id'), nullable=False)
    opening_reading = db.Column(db.Float, nullable=False)
    closing_reading = db.Column(db.Float, nullable=False)
    cash_sales = db.Column(db.Float, default=0.0)
    digital_sales = db.Column(db.Float, default=0.0)
    date = db.Column(db.Date, nullable=False)

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fuel_id = db.Column(db.Integer, db.ForeignKey('fuel_type.id'), nullable=False)
    quantity_received = db.Column(db.Float, nullable=False)
    invoice_number = db.Column(db.String(50))
    density_observed = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False)