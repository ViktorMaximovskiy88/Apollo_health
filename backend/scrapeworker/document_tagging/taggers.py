from dataclasses import dataclass

from backend.scrapeworker.document_tagging.indication_tagging import indication_tagger
from backend.scrapeworker.document_tagging.therapy_tagging import therapy_tagger


@dataclass
class Taggers:
    indication: indication_tagger
    therapy: therapy_tagger
