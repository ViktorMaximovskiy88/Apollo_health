import { BaseDocument } from '../../common/types';

export interface DocumentQuery {
  scrape_task_id?: string | null;
  site_id?: string | null;
  logical_document_id?: string | null;
  automated_content_extraction?: boolean | null;
}

export interface RetrievedDocument extends BaseDocument {
  _id: string;
  site_id: string;
  scrape_task_id: string;
  logical_document_id?: string;
  logical_document_version?: number;
  document_type?: string;
  doc_type_confidence?: number;
  first_collected_date: string;
  disabled: boolean;
  url: string;
  checksum: string;
  name?: string;
  metadata?: { [key: string]: string };
  context_metadata?: { [key: string]: string };
  effective_date?: string;
  end_date?: string;
  last_updated_date?: string;
  last_reviewed_date?: string;
  next_review_date?: string;
  next_update_date?: string;
  published_date?: string;
  identified_dates?: string[];
  base_url: string;
  lang_code: string;
  file_extension: string;
  document_file: any;
  automated_content_extraction: boolean;
  automated_content_extraction_class: string;
}
