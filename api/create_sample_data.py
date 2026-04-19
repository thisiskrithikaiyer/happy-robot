from app import app, db
from models import Load
from datetime import datetime, timedelta
import random

def create_sample_loads():
    loads_data = [
        {
            'load_id': 'L001',
            'origin': 'Los Angeles, CA',
            'destination': 'New York, NY',
            'pickup_datetime': datetime.now() + timedelta(days=1),
            'delivery_datetime': datetime.now() + timedelta(days=3),
            'equipment_type': 'Dry Van',
            'loadboard_rate': 2500.0,
            'notes': 'Standard freight',
            'weight': 15000.0,
            'commodity_type': 'Electronics',
            'num_of_pieces': 50,
            'miles': 2450.0,
            'dimensions': '48x40x40'
        },
        # Add 14 more similar
        {
            'load_id': 'L002',
            'origin': 'Chicago, IL',
            'destination': 'Houston, TX',
            'pickup_datetime': datetime.now() + timedelta(days=2),
            'delivery_datetime': datetime.now() + timedelta(days=4),
            'equipment_type': 'Refrigerated',
            'loadboard_rate': 1800.0,
            'notes': 'Perishable goods',
            'weight': 12000.0,
            'commodity_type': 'Food',
            'num_of_pieces': 30,
            'miles': 1080.0,
            'dimensions': '48x40x40'
        },
        {
            'load_id': 'L003',
            'origin': 'Seattle, WA',
            'destination': 'Denver, CO',
            'pickup_datetime': datetime.now() + timedelta(days=1),
            'delivery_datetime': datetime.now() + timedelta(days=2),
            'equipment_type': 'Flatbed',
            'loadboard_rate': 1200.0,
            'notes': 'Heavy machinery',
            'weight': 20000.0,
            'commodity_type': 'Machinery',
            'num_of_pieces': 5,
            'miles': 1300.0,
            'dimensions': '48x96x96'
        },
        # Continue for 15 total
    ]
    # Generate more randomly
    for i in range(4, 16):
        load = {
            'load_id': f'L{i:03d}',
            'origin': random.choice(['LA', 'NY', 'Chicago', 'Houston']),
            'destination': random.choice(['NY', 'LA', 'Denver', 'Seattle']),
            'pickup_datetime': datetime.now() + timedelta(days=random.randint(1,5)),
            'delivery_datetime': datetime.now() + timedelta(days=random.randint(3,7)),
            'equipment_type': random.choice(['Dry Van', 'Refrigerated', 'Flatbed']),
            'loadboard_rate': random.uniform(1000, 3000),
            'notes': 'Sample load',
            'weight': random.uniform(5000, 25000),
            'commodity_type': random.choice(['Electronics', 'Food', 'Machinery', 'Clothing']),
            'num_of_pieces': random.randint(10, 100),
            'miles': random.uniform(500, 2500),
            'dimensions': '48x40x40'
        }
        loads_data.append(load)

    for data in loads_data:
        load = Load(**data)
        db.session.add(load)
    db.session.commit()
    print("Sample loads created")

if __name__ == '__main__':
    with app.app_context():
        create_sample_loads()