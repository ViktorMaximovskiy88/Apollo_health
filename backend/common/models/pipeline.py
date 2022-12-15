from datetime import datetime

from beanie import PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class PipelineStage(BaseModel):
    version: int
    version_at: datetime
    is_locked: bool = False


# the global entry
class PipelineRegistryStage(PipelineStage):
    version_by: PydanticObjectId
    notes: str = ""


class PipelineRegistry(BaseDocument):
    content: PipelineRegistryStage
    date: PipelineRegistryStage
    doc_type: PipelineRegistryStage
    tag: PipelineRegistryStage
    lineage: PipelineRegistryStage

    @classmethod
    async def fetch(cls):
        return await cls.find_one()


# for the target objects
class DocPipelineStages(BaseModel):
    content: PipelineStage | None
    date: PipelineStage | None
    doc_type: PipelineStage | None
    tag: PipelineStage | None

    @classmethod
    def is_stage_valid(cls, doc_stage: PipelineStage, registry_stage: PipelineStage):
        return doc_stage and doc_stage.version == registry_stage.version


class SitePipelineStages(BaseModel):
    lineage: PipelineStage | None
    all_documents: DocPipelineStages | None
