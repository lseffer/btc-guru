from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime


@dataclass(frozen=True)
class InfluxdbModel():
    measurement: str = ""
    tags: Dict = field(default_factory=lambda: {})
    time: float = datetime.utcnow().timestamp()
    fields: Dict = field(default_factory=lambda: {})

    @property
    def schema(self):
        return {
            "measurement": self.measurement,
            "tags": self.tags,
            "time": self.time,
            "fields": self.fields
        }
