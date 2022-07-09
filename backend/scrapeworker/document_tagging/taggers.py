from dataclasses import dataclass

from scrapeworker.document_tagging.indication_tagging import IndicationTagger
from scrapeworker.document_tagging.therapy_tagging import TherapyTagger


@dataclass
class Taggers:
    indication: IndicationTagger
    therapy: TherapyTagger
