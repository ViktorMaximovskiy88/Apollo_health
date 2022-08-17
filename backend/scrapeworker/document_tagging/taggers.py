from dataclasses import dataclass

from backend.scrapeworker.document_tagging.indication_tagging import IndicationInstance
from backend.scrapeworker.document_tagging.therapy_tagging import TherapyInstance


@dataclass
class Taggers:
    indication: IndicationInstance
    therapy: TherapyInstance
