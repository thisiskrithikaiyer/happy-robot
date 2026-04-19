import logging
from flask import Blueprint, request, jsonify, abort
from models import db, Load, Offer
from utils import verify_carrier
from functools import wraps
from config import Config

logging.basicConfig(level=logging.INFO)

api = Blueprint('api', __name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != Config.API_KEY:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

@api.route('/loads', methods=['GET'])
@require_api_key
def get_loads():
    logging.info(f"[search_loads] params: origin={request.args.get('origin')} destination={request.args.get('destination')} equipment_type={request.args.get('equipment_type')}")
    query = Load.query
    if request.args.get('origin'):
        query = query.filter(Load.origin.ilike(f"%{request.args.get('origin')}%"))
    if request.args.get('destination'):
        query = query.filter(Load.destination.ilike(f"%{request.args.get('destination')}%"))
    if request.args.get('equipment_type'):
        query = query.filter(Load.equipment_type.ilike(f"%{request.args.get('equipment_type')}%"))
    # Add more filters as needed
    loads = query.all()
    return jsonify([{
        'load_id': l.load_id,
        'origin': l.origin,
        'destination': l.destination,
        'pickup_datetime': l.pickup_datetime.isoformat(),
        'delivery_datetime': l.delivery_datetime.isoformat(),
        'equipment_type': l.equipment_type,
        'loadboard_rate': l.loadboard_rate,
        'notes': l.notes,
        'weight': l.weight,
        'commodity_type': l.commodity_type,
        'num_of_pieces': l.num_of_pieces,
        'miles': l.miles,
        'dimensions': l.dimensions
    } for l in loads])

@api.route('/offers', methods=['POST'])
@require_api_key
def post_offer():
    data = request.json
    import uuid
    price = data.get('negotiated_price')
    try:
        price = float(price) if price else None
    except (ValueError, TypeError):
        price = None
    offer = Offer(
        load_id=data.get('load_id') or str(uuid.uuid4())[:8],
        carrier_mc=data.get('carrier_mc', 'UNKNOWN'),
        negotiated_price=price,
        outcome=data.get('outcome', 'not_agreed'),
        sentiment=data.get('sentiment', 'neutral'),
        origin=data.get('origin'),
        destination=data.get('destination'),
        equipment_type=data.get('equipment_type')
    )
    db.session.add(offer)
    db.session.commit()
    return jsonify({'message': 'Offer logged'}), 201

@api.route('/verify_carrier', methods=['GET'])
@require_api_key
def verify():
    mc = request.args.get('mc')
    if not mc:
        return jsonify({'eligible': False}), 400
    eligible = verify_carrier(mc)
    return jsonify({'eligible': eligible})

@api.route('/offers', methods=['DELETE'])
@require_api_key
def clear_offers():
    Offer.query.delete()
    db.session.commit()
    return jsonify({'message': 'All offers cleared'})

@api.route('/metrics', methods=['GET'])
@require_api_key
def get_metrics():
    total_calls = Offer.query.count()
    agreed = Offer.query.filter_by(outcome='agreed').count()
    success_rate = agreed / total_calls if total_calls > 0 else 0
    avg_price = db.session.query(db.func.avg(Offer.negotiated_price)).filter(Offer.negotiated_price.isnot(None)).scalar() or 0
    min_price = db.session.query(db.func.min(Offer.negotiated_price)).filter(Offer.negotiated_price.isnot(None)).scalar() or 0
    max_price = db.session.query(db.func.max(Offer.negotiated_price)).filter(Offer.negotiated_price.isnot(None)).scalar() or 0
    
    sentiment_counts = db.session.query(Offer.sentiment, db.func.count(Offer.sentiment)).group_by(Offer.sentiment).all()
    sentiment = {s: c for s, c in sentiment_counts}
    
    outcome_counts = db.session.query(Offer.outcome, db.func.count(Offer.outcome)).group_by(Offer.outcome).all()
    outcomes = {o: c for o, c in outcome_counts}
    
    # Top loads
    top_loads = db.session.query(Offer.load_id, db.func.count(Offer.load_id).label('count')).group_by(Offer.load_id).order_by(db.desc('count')).limit(5).all()
    top_loads_dict = [{'load_id': l[0], 'calls': l[1]} for l in top_loads]
    
    unique_carriers = db.session.query(db.func.count(db.distinct(Offer.carrier_mc))).scalar()

    # Popular lanes
    lane_data = db.session.query(
        Offer.origin, Offer.destination,
        db.func.count(Offer.id).label('calls'),
        db.func.sum(db.case((Offer.outcome == 'agreed', 1), else_=0)).label('booked')
    ).filter(Offer.origin.isnot(None)).group_by(Offer.origin, Offer.destination).order_by(db.desc('calls')).limit(5).all()
    lanes = [{'lane': f"{r.origin} → {r.destination}", 'calls': r.calls, 'booked': int(r.booked or 0)} for r in lane_data]

    # Equipment type stats
    equipment_data = db.session.query(
        Offer.equipment_type,
        db.func.count(Offer.id).label('calls'),
        db.func.sum(db.case((Offer.outcome == 'agreed', 1), else_=0)).label('booked')
    ).filter(Offer.equipment_type.isnot(None)).group_by(Offer.equipment_type).order_by(db.desc('calls')).all()
    equipment = [{'type': r.equipment_type, 'calls': r.calls, 'booked': int(r.booked or 0)} for r in equipment_data]

    return jsonify({
        'total_calls': total_calls,
        'success_rate': success_rate,
        'unique_carriers': unique_carriers,
        'avg_negotiated_price': float(avg_price),
        'min_negotiated_price': float(min_price),
        'max_negotiated_price': float(max_price),
        'sentiment': sentiment,
        'outcomes': outcomes,
        'top_loads': top_loads_dict,
        'lanes': lanes,
        'equipment': equipment
    })