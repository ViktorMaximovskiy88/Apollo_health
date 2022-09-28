from datetime import datetime

from beanie import PydanticObjectId


class DocumentMixins:
    def set_first_collected(self):
        location = get_first_collected(self)
        self.first_collected_date = location.first_collected_date

    def set_last_collected(self):
        location = get_last_collected(self)
        self.last_collected_date = location.last_collected_date

    def set_final_effective_date(self):
        self.final_effective_date = calc_final_effective_date(self)

    def find_site_index(self, site_id: PydanticObjectId):
        return next((i for i, item in enumerate(self.locations) if item.site_id == site_id), -1)

    def get_site_location(self, site_id):
        location_index = find_site_index(self, site_id)
        return self.locations[location_index] if location_index > -1 else None


# TODO maybe remove these... they had need maybe now they dont...
def get_first_collected(doc):
    return min(doc.locations, key=lambda location: location.first_collected_date)


def get_last_collected(doc):
    return max(doc.locations, key=lambda location: location.last_collected_date)


def calc_final_effective_date(doc) -> datetime | None:
    computeFromFields: list[datetime] = []
    if doc.effective_date:
        computeFromFields.append(doc.effective_date)
    if doc.last_reviewed_date:
        computeFromFields.append(doc.last_reviewed_date)
    if doc.last_updated_date:
        computeFromFields.append(doc.last_updated_date)

    final_effective_date = (
        max(computeFromFields) if len(computeFromFields) > 0 else doc.first_collected_date
    )
    return final_effective_date


def find_site_index(document, site_id: PydanticObjectId):
    return next((i for i, item in enumerate(document.locations) if item.site_id == site_id), -1)


def get_site_location(document, site_id: PydanticObjectId):
    location_index = find_site_index(document, site_id)
    return document.locations[location_index] if location_index > -1 else None
