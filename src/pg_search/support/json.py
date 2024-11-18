import json
import datetime
import decimal
import uuid


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        match type(obj):
            case decimal.Decimal:
                if obj == obj.to_integral():
                    return int(obj.quantize(decimal.Decimal(1)))
                else:
                    return float(obj.normalize())
            case datetime.datetime:
                return obj.isoformat()
            case datetime.date:
                return obj.isoformat()
            case uuid.UUID:
                return str(obj)
        return json.JSONEncoder.default(self, obj)
