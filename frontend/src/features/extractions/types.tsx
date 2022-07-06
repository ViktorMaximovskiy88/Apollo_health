export interface ExtractionTask {
  _id: string;
  site_id: string;
  scrape_task_id: string;
  retrieved_document_id: string;
  worker_id?: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: string;
  extraction_count?: number;
}

export interface ContentExtractionResult {
  _id: string;
  site_id: string;
  scrape_task_id: string;
  retrieved_document_id: string;
  content_extraction_task_id: string;
  first_collected_date: string;
  result: {};
  page: number;
  row: number;
}
