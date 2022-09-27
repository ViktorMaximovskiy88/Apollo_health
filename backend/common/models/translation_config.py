from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class TranslationMapping(BaseModel):
    pattern: str = ""
    translation: str


class TranslationRule(BaseModel):
    field: str
    pattern: str = ""
    separator: str = ""
    value: str = ""
    capture_all: bool = False
    mappings: list[TranslationMapping]


class ColumnTranslation(BaseModel):
    column: str
    rules: list[TranslationRule]


class TableDetectionConfig(BaseModel):
    start_text: str = ""
    start_page: int = 0
    end_text: str = ""
    end_page: int = 0
    required_header_text: str | None = None
    excluded_header_text: str | None = None


class TableExtractionConfig(BaseModel):
    required_columns: list[str] = []
    banned_columns: list[str] = []
    merge_on_missing_columns: list[str] = []
    start_table_text: str = ""
    end_table_text: str = ""
    merge_strategy: str = "DOWN"
    snap_tolerance: int = 3
    intersection_tolerance: int = 3
    table_shape: str = "lines"
    explicit_headers: list[str] = []
    explicit_column_lines: list[str] = []
    explicit_column_lines_only: bool = False
    skip_rows: int = 0
    skip_rows_first_table_only: bool = False


class TableTranslationConfig(BaseModel):
    product_column: list[str] = []
    column_rules: list[ColumnTranslation] = []


class TableSampleConfig(BaseModel):
    site_id: PydanticObjectId | None = None
    doc_id: PydanticObjectId | None = None


class TranslationConfig(BaseDocument):
    name: str = ""
    detection: TableDetectionConfig = TableDetectionConfig()
    extraction: TableExtractionConfig = TableExtractionConfig()
    translation: TableTranslationConfig = TableTranslationConfig()
    sample: TableSampleConfig = TableSampleConfig()


class UpdateTableDetectionConfig(BaseModel):
    start_text: str | None = None
    start_page: int | None = None
    end_text: str | None = None
    end_page: int | None = None
    required_header_text: str | None = None
    excluded_header_text: str | None = None


class UpdateTableExtractionConfig(BaseModel):
    required_columns: list[str] | None = None
    banned_columns: list[str] = []
    merge_on_missing_columns: list[str] | None = None
    merge_strategy: str | None = None
    start_table_text: str = ""
    end_table_text: str = ""
    snap_tolerance: int | None = None
    intersection_tolerance: int | None = None
    table_shape: str | None = None
    explicit_headers: list[str] | None = None
    explicit_column_lines: list[str] | None = None
    explicit_column_lines_only: bool = False
    skip_rows: int | None = None
    skip_rows_first_table_only: bool | None = None


class UpdateTableTranslationConfig(BaseModel):
    product_column: list[str] | None = None
    column_rules: list[ColumnTranslation] | None = None


class UpdateTableSampleConfig(BaseModel):
    site_id: PydanticObjectId | None = None
    doc_id: PydanticObjectId | None = None


class UpdateTranslationConfig(BaseModel):
    name: str | None = None
    detection: UpdateTableDetectionConfig | None = None
    extraction: UpdateTableExtractionConfig | None = None
    translation: UpdateTableTranslationConfig | None = None
    sample: UpdateTableSampleConfig | None = None
