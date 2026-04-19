import os
import requests
from config import Config

def verify_carrier(mc_number):
    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{mc_number}?webKey={Config.FMCSA_KEY}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            carrier = data.get('content', {}).get('carrier', {})
            return carrier.get('allowedToOperate') == 'Y'
    except Exception:
        pass

    # Fall back to eligible when FMCSA key is not configured (demo mode)
    if os.getenv('FMCSA_DEMO_MODE', 'false').lower() == 'true':
        return True
    return False