from app import create_app
from app.models import db, FuelType, Tank

app = create_app()

with app.app_context():
    # Add Fuel Types
    petrol = FuelType(name="Petrol", base_price=109.45)
    diesel = FuelType(name="Diesel", base_price=97.23)
    power = FuelType(name="Power", base_price=115.10)
    
    db.session.add_all([petrol, diesel, power])
    
    # Add Initial Tanks (Assuming standard capacities)
    t1 = Tank(fuel_id=1, capacity=20000, current_dip_level=15000)
    t2 = Tank(fuel_id=2, capacity=20000, current_dip_level=12000)
    
    db.session.add_all([t1, t2])
    db.session.commit()
    print("Database seeded with HP Fuel types!")