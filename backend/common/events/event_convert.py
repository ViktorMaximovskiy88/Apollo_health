import attr
from bson.json_util import dumps


class EventConvert:
    
    def __init__(self, document, event_type="new"):
      self.document = document
      self.event_type = event_type

    
    def convert(self):
       return dumps(self.document)
        