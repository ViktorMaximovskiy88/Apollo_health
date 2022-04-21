import { BaseDocument } from "../types";

export interface DocumentQuery {
  scrape_task_id?: string | null;
  site_id?: string | null;
  logical_document_id?: string | null;
}

export interface RetrievedDocument extends BaseDocument {
    site_id: string;
    scrape_task_id: string;
    logical_document_id?: string;
    logical_document_version?: number;
    document_type?: string;
    collection_time: string;
    disabled: boolean;
    url: string;
    checksum: string;
    name?: string;
    metadata?: { [key: string]: string };
    effective_date?: string;
    identified_dates?: string[];
}