import { BaseDocument } from '../../common/types';

export interface DocumentQuery {
  scrape_task_id?: string | null;
  site_id?: string | null;
  logical_document_id?: string | null;
  automated_content_extraction?: boolean | null;
}

export interface RetrievedDocument extends BaseDocument {
  site_id: string;
  scrape_task_id: string;
  logical_document_id?: string;
  logical_document_version?: number;
  document_type?: string;
  doc_type_confidence?: number;
  collection_time: string;
  disabled: boolean;
  url: string;
  checksum: string;
  name?: string;
  metadata?: { [key: string]: string };
  context_metadata?: { [key: string]: string };
  effective_date?: string;
  identified_dates?: string[];
  base_url: string;
  lang_code: string;

  automated_content_extraction: boolean;
  automated_content_extraction_class: string;
}
