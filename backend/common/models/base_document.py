from datetime import datetime
from beanie import Document


class BaseDocument(Document):
    def created(self) -> datetime:
        if not self.id:
            return datetime.utcfromtimestamp(0)
        return self.id.generation_time
