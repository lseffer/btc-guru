from flask_jsontools import DynamicJSONEncoder
from datetime import date, datetime
from itertools import zip_longest
from typing import Iterable


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


def grouper(iterable: Iterable, n: int, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
