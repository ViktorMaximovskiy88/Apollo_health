from bson.json_util import dumps


class EventConvert:
    def __init__(self, document, event_type="new"):
        self.document = document
        self.event_type = event_type

    def convert(self):
        # Since a document can have 1000+ tags, exclude all tags.
        # Otherwise, payload to big.
        # TODO: Once event model api defined,
        # refactor into DocumentEvent model which matches api definition.
        if "therapy_tags" in self.document:
            self.document["therapy_tags"] = []
        if "indication_tags" in self.document:
            self.document["indication_tags"] = []
        if "tags" in self.document:
            self.document["tags"] = []

        return dumps(self.document)
