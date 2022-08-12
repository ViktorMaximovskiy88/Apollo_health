from datetime import datetime

from backend.common.models.doc_document import DocDocument


def calc_final_effective_date(doc: DocDocument) -> datetime:
    computeFromFields = []

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
