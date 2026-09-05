from qdrant_client.models import DatetimeRange, Filter, FieldCondition, MatchAny, MatchValue, Range


from datetime import datetime
def is_datetime_str(val):
    if not isinstance(val, str):
        return False
    try:
        datetime.fromisoformat(val.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def build_payload_filter(payload_filter: dict) -> Filter:
    must_conditions = []
    for key, value in payload_filter.items():
        if isinstance(value, dict) and any(k in value for k in ["gt", "gte", "lt", "lte"]):
            if any(is_datetime_str(v) for v in value.values() if v is not None):
                must_conditions.append(FieldCondition(key=key, range=DatetimeRange(
                    gte=value.get("gte"), gt=value.get("gt"),
                    lte=value.get("lte"), lt=value.get("lt"))))
            else:
                must_conditions.append(FieldCondition(key=key, range=Range(
                    gte=value.get("gte"), gt=value.get("gt"),
                    lte=value.get("lte"), lt=value.get("lt"))))
        elif isinstance(value, list):
            must_conditions.append(FieldCondition(key=key, match=MatchAny(any=value)))
        else:
            must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
    return Filter(must=must_conditions)