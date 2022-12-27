from datetime import date, datetime

from beanie import PydanticObjectId


class DocumentMixins:
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


def as_naive_date(_datetime: datetime) -> date:
    return (
        _datetime.replace(
            tzinfo=None,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        if _datetime
        else _datetime
    )


# TODO: i dont love this, but beanie wasnt having `date` (somewhere on the write side)
# will investigate later, but poor mans date for now
def cast_dates(doc):
    # Pydantic BaseModel can differentiate between unset and None
    # and we want to keep that distinction, so don't set to None if already None
    if doc.effective_date:
        doc.effective_date = as_naive_date(doc.effective_date)
    if doc.last_reviewed_date:
        doc.last_reviewed_date = as_naive_date(doc.last_reviewed_date)
    if doc.last_updated_date:
        doc.last_updated_date = as_naive_date(doc.last_updated_date)
    if doc.next_review_date:
        doc.next_review_date = as_naive_date(doc.next_review_date)
    if doc.next_update_date:
        doc.next_update_date = as_naive_date(doc.next_update_date)
    if doc.published_date:
        doc.published_date = as_naive_date(doc.published_date)
    if doc.end_date:
        doc.end_date = as_naive_date(doc.end_date)


def calc_final_effective_date(doc) -> datetime | None:
    computeFromFields: list[datetime] = []

    # abusing the fact that we always call this.. would like to wrap into pydantic/beanie
    cast_dates(doc)

    if doc.effective_date:
        computeFromFields.append(doc.effective_date)
    if doc.last_reviewed_date:
        computeFromFields.append(doc.last_reviewed_date)
    if doc.last_updated_date:
        computeFromFields.append(doc.last_updated_date)

    final_effective_date = (
        max(computeFromFields) if len(computeFromFields) > 0 else doc.first_collected_date
    )

    return as_naive_date(final_effective_date)


def find_site_index(document, site_id: PydanticObjectId) -> int:
    return next((i for i, item in enumerate(document.locations) if item.site_id == site_id), -1)


def get_site_location(document, site_id: PydanticObjectId):
    location_index = find_site_index(document, site_id)
    return document.locations[location_index] if location_index > -1 else None
