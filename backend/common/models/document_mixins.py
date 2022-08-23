from datetime import datetime
from typing import TypeVar

from beanie import PydanticObjectId

from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument

T = TypeVar(
    "T", bound=DocDocument | UpdateDocDocument | RetrievedDocument | UpdateRetrievedDocument
)


class DocumentMixins:
    def set_computed_values(self):
        self.set_first_collected()
        self.set_last_collected()
        self.set_final_effective_date()

    def set_first_collected(self: T):
        self.first_collected_date = get_first_collected(self)

    def set_last_collected(self: T):
        self.last_collected_date = get_last_collected(self)

    def set_final_effective_date(self: T):
        self.final_effective_date = calc_final_effective_date(self)

    def find_site_index(self: T, site_id: PydanticObjectId):
        return next((i for i, item in enumerate(self.locations) if item.site_id == site_id), -1)

    def get_site_location(self: T, site_id):
        location_index = find_site_index(site_id, self)
        return self.locations[location_index] if location_index > -1 else None


# TODO maybe remove these... they had need maybe now they dont...


def get_first_collected(doc: T):
    return min(doc.locations, key=lambda location: location.first_collected_date)


def get_last_collected(doc: T):
    return max(doc.locations, key=lambda location: location.last_collected_date)


def calc_final_effective_date(doc: T) -> datetime | None:
    computeFromFields: list[datetime] = []
    if doc.effective_date:
        computeFromFields.append(doc.effective_date)
    if doc.last_reviewed_date:
        computeFromFields.append(doc.last_reviewed_date)
    if doc.last_updated_date:
        computeFromFields.append(doc.last_updated_date)

    final_effective_date = (
        max(computeFromFields) if len(computeFromFields) > 0 else doc.last_collected_date
    )
    return final_effective_date


def find_site_index(document: T, site_id: PydanticObjectId):
    return next((i for i, item in enumerate(document.locations) if item.site_id == site_id), -1)


def get_site_location(document: T, site_id: PydanticObjectId):
    location_index = find_site_index(site_id, document)
    return document.locations[location_index] if location_index > -1 else None
