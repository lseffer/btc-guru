from flask_jsontools import DynamicJSONEncoder
from datetime import date, datetime


class ApiJSONEncoder(DynamicJSONEncoder):
    def default(self, o):
        # Custom formats
        if isinstance(o, datetime):
            return o.isoformat(' ')
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)

        # Fallback
        return super(DynamicJSONEncoder, self).default(o)
