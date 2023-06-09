import { BaseDocument } from '../../common';

export interface TranslationMapping {
  pattern: string;
  translation: string;
}

export interface TranslationRule {
  field: string; // 'Tier', 'PA', 'QL', 'SP' etc.
  pattern: string;
  value: string;
  capture_all: string;
  separator: string;
  separator2: string;
  mappings: TranslationMapping[];
}

export interface ColumnTranslation {
  column: string;
  rules: TranslationRule[];
}

export interface TableDetectionConfig {
  start_text: string;
  start_page: number;
  end_text: string;
  end_page: number;
  required_header_text?: string;
  exclude_header_text?: string;
}

export interface TableExtractionConfig {
  required_columns: string[];
  banned_columns: string[];
  merge_on_missing_columns: string[];
  merge_strategy: string;
  start_table_text: string;
  end_table_text: string;
  snap_tolerance: number;
  intersection_tolerance: number;
  table_shape: string;
  explicit_headers: string[];
  explicit_column_lines: string[];
  explicit_column_lines_only: boolean;
  skip_rows: number;
  skip_row_first_table_only: boolean;
  max_font_size: number;
}

export interface TableTranslationConfig {
  product_columns: string[];
  column_rules: ColumnTranslation[];
}

export interface TableSampleConfig {
  site_id?: string;
  doc_id?: string;
}

export interface TranslationConfig extends BaseDocument {
  name: string;
  detection: TableDetectionConfig;
  extraction: TableExtractionConfig;
  translation: TableTranslationConfig;
  sample: TableSampleConfig;
}
