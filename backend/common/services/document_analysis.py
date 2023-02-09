from pymongo import InsertOne, UpdateOne

from backend.common.models.doc_document import DocDocument, PydanticObjectId, SiteDocDocument
from backend.common.models.document_analysis import (
    DocumentAnalysis,
    DocumentAnalysisHeader,
    DocumentAttrs,
)
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.shared import get_unique_focus_tags, get_unique_reference_tags
from backend.scrapeworker.common.lineage_parser import (
    guess_month_abbr,
    guess_month_name,
    guess_month_part,
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)
from backend.scrapeworker.common.utils import compact, tokenize_filename, tokenize_url


def build_attr_model(input: str | None) -> DocumentAttrs:
    return DocumentAttrs(
        state_abbr=guess_state_abbr(input),
        state_name=guess_state_name(input),
        year_part=guess_year_part(input),
        month_abbr=guess_month_abbr(input),
        month_name=guess_month_name(input),
        month_part=guess_month_part(input),
    )


# TODO tweak logic, for now its all or nothing
#  url, context, document
def consensus_attr(model: DocumentAnalysis, attr: str):
    all_attrs = compact(
        [
            getattr(model.filename, attr),
            getattr(model.pathname, attr),
            # TODO file and path are easier to guess due to human formatting of paths/urls/files
            getattr(model.element, attr),
            getattr(model.parent, attr),
            getattr(model.siblings, attr),
        ]
    )
    consensus = list(set(all_attrs))
    return consensus[0] if len(consensus) == 1 else None


async def upsert_for_location(doc: DocDocument, site_id: PydanticObjectId):
    doc_analysis = await DocumentAnalysis.find_one(
        {
            "doc_document_id": doc.id,
            "site_id": site_id,
        }
    )

    site_doc_doc = doc.for_site(site_id)
    doc_analysis = build_doc_analysis(site_doc_doc, doc_analysis)
    await doc_analysis.save()


async def upsert_for_doc_doc(doc: DocDocument):

    doc_analyses = await DocumentAnalysis.find(
        {"doc_document_id": doc.id},
        projection_model=DocumentAnalysisHeader,
    ).to_list()

    batch = []
    for location in doc.locations:
        doc_analysis = next((doc for doc in doc_analyses if doc.site_id == location.site_id), None)
        if not doc_analysis:
            site_doc_doc = doc.for_site(location.site_id)
            doc_analysis = build_doc_analysis(site_doc_doc, None)
            batch.append(InsertOne(doc_analysis.dict()))
        else:
            batch.append(
                UpdateOne(
                    {"_id": doc_analysis.id},
                    {
                        "$set": {
                            "previous_doc_doc_id": doc.previous_doc_doc_id,
                            "lineage_id": doc.lineage_id,
                            "name": doc.name,
                            "final_effective_date": calc_final_effective_date(doc),
                            "document_type": doc.document_type,
                            "focus_therapy_tags": get_unique_focus_tags(doc.therapy_tags),
                            "focus_indication_tags": get_unique_focus_tags(doc.indication_tags),
                            "ref_therapy_tags": get_unique_reference_tags(doc.therapy_tags),
                            "ref_indication_tags": get_unique_reference_tags(doc.indication_tags),
                        }
                    },
                )
            )

    if not batch:
        raise Exception("No document analysis for doc_doc_id={doc.id}")

    await DocumentAnalysis.get_motor_collection().bulk_write(batch)


def build_doc_analysis(
    doc: SiteDocDocument, doc_analysis: DocumentAnalysis | None
) -> DocumentAnalysis:
    if doc_analysis is None:
        doc_analysis = DocumentAnalysis(
            doc_document_id=doc.id,
            retrieved_document_id=doc.retrieved_document_id,  # TODO RIP rt doc
            previous_doc_doc_id=doc.previous_doc_doc_id,
            lineage_id=doc.lineage_id,
            confidence=doc.lineage_confidence,
            site_id=doc.site_id,
        )

    # immutable
    # TODO prob remove upon a doc analysis wipe (going to say we do this...)
    doc_analysis.doc_document_id = doc.id

    # frontend or backend changeable
    doc_analysis.previous_doc_doc_id = doc.previous_doc_doc_id
    doc_analysis.lineage_id = doc.lineage_id
    doc_analysis.name = doc.name
    doc_analysis.final_effective_date = calc_final_effective_date(doc)
    doc_analysis.document_type = doc.document_type

    doc_analysis.focus_therapy_tags = get_unique_focus_tags(doc.therapy_tags)
    doc_analysis.focus_indication_tags = get_unique_focus_tags(doc.indication_tags)
    doc_analysis.ref_therapy_tags = get_unique_reference_tags(doc.therapy_tags)
    doc_analysis.ref_indication_tags = get_unique_reference_tags(doc.indication_tags)

    # backend changeable
    doc_analysis.file_size = doc.file_size
    doc_analysis.doc_vectors = doc.doc_vectors
    doc_analysis.token_count = doc.token_count
    doc_analysis.element_text = doc.link_text

    doc_analysis.url_focus_therapy_tags = get_unique_focus_tags(doc.url_therapy_tags)
    doc_analysis.url_focus_indication_tags = get_unique_focus_tags(doc.url_indication_tags)

    doc_analysis.link_focus_therapy_tags = get_unique_focus_tags(doc.link_therapy_tags)
    doc_analysis.link_focus_indication_tags = get_unique_focus_tags(doc.link_indication_tags)

    [*path_parts, filename] = tokenize_url(doc.url)
    doc_analysis.filename_text = filename
    doc_analysis.pathname_text = "/".join(path_parts)
    doc_analysis.pathname_tokens = compact(path_parts)
    doc_analysis.filename_tokens = tokenize_filename(filename)

    doc_analysis.pathname = build_attr_model(doc_analysis.pathname_text)
    doc_analysis.filename = build_attr_model(doc_analysis.filename_text)
    doc_analysis.element = build_attr_model(doc_analysis.element_text)
    doc_analysis.parent = build_attr_model(doc_analysis.parent_text)
    doc_analysis.siblings = build_attr_model(doc_analysis.siblings_text)

    doc_analysis.state_abbr = consensus_attr(doc_analysis, "state_abbr")
    doc_analysis.state_name = consensus_attr(doc_analysis, "state_name")
    doc_analysis.month_abbr = consensus_attr(doc_analysis, "month_abbr")
    doc_analysis.month_name = consensus_attr(doc_analysis, "month_name")
    doc_analysis.year_part = (
        int(year_part) if (year_part := consensus_attr(doc_analysis, "year_part")) else 0
    )

    return doc_analysis
