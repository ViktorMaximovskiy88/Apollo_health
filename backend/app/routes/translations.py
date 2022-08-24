import tempfile

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import Response, StreamingResponse

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    delete_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.models.doc_document import DocDocument
from backend.common.models.translation_config import TranslationConfig, UpdateTranslationConfig
from backend.common.models.user import User
from backend.parseworker.extractor import TableContentExtractor

router = APIRouter(
    prefix="/translations",
    tags=["Translations"],
)


async def get_target(id: PydanticObjectId) -> TranslationConfig:
    config = await TranslationConfig.get(id)
    if not config:
        raise HTTPException(
            detail=f"Translation Config {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return config


async def get_doc_document(doc_id: PydanticObjectId) -> DocDocument:
    doc = await DocDocument.get(doc_id)
    if not doc:
        raise HTTPException(
            detail=f"Doc Document {doc_id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return doc


@router.get(
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_translations(
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = TranslationConfig.find({})
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/{id}",
    response_model=TranslationConfig,
    dependencies=[Security(get_current_user)],
)
async def read_translation_config(
    target: TranslationConfig = Depends(get_target),
):
    return target


@router.get("/sample-doc/{doc_id}", status_code=status.HTTP_201_CREATED)
async def get_doc_sample(
    config: TranslationConfig = Depends(lambda config: TranslationConfig.parse_raw(config)),
    doc: DocDocument = Depends(get_doc_document),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    extractor = TableContentExtractor(doc, config)
    sample_key = extractor.create_doc_sample()
    stream = extractor.client.read_object_stream(sample_key)
    return StreamingResponse(stream, media_type="application/pdf")


@router.get("/sample-doc/{doc_id}/table-image")
async def create_doc_sample_table_image(
    config: TranslationConfig = Depends(lambda config: TranslationConfig.parse_raw(config)),
    doc: DocDocument = Depends(get_doc_document),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    extractor = TableContentExtractor(doc, config)
    with extractor.sample_doc_page() as page:
        im = page.to_image(resolution=150)
        page_image = im.debug_tablefinder(extractor.tablefinder_config())
        with tempfile.TemporaryFile("wb+") as file:
            page_image.save(file, format="PNG")
            file.seek(0)
            return Response(content=file.read(), media_type="image/png")


@router.get("/sample-doc/{doc_id}/extract")
async def create_doc_sample_table_extraction(
    config: TranslationConfig = Depends(lambda config: TranslationConfig.parse_raw(config)),
    doc: DocDocument = Depends(get_doc_document),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    extractor = TableContentExtractor(doc, config)
    with extractor.sample_doc_page() as page:
        tables = extractor.extract_clean_tables(page)
        return tables


@router.get("/sample-doc/{doc_id}/translate")
async def create_doc_sample_table_translation(
    config: TranslationConfig = Depends(lambda config: TranslationConfig.parse_raw(config)),
    doc: DocDocument = Depends(get_doc_document),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    translations = []
    extractor = TableContentExtractor(doc, config)
    with extractor.sample_doc_page() as page:
        tables = extractor.extract_clean_tables(page)
        for (_, _, _, _, t) in extractor.translate_tables(tables):
            translations.append(t)
    return translations


@router.put("/", response_model=TranslationConfig, status_code=status.HTTP_201_CREATED)
async def create_translation(
    config: TranslationConfig,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await create_and_log(logger, current_user, config)
    return config


@router.delete("/{id}")
async def delete_translation(
    target: User = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # TODO Prevent delete of translations that are in use, return list of uses
    await delete_and_log(logger, current_user, target)
    return {"success": True}


@router.post("/{id}", response_model=TranslationConfig)
async def update_translation_config(
    updates: UpdateTranslationConfig,
    target: TranslationConfig = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated
