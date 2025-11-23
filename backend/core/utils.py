import uuid
from datetime import datetime, timezone

def gen_uuid():
    return str(uuid.uuid4())

def now_utc():
    return  datetime.now(timezone.utc)

def to_str(val):
    return str(val) if val else None

def parse_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
    
def clean_str(val):
    if isinstance(val,str):
        return val.strip()
    else:
        return None
