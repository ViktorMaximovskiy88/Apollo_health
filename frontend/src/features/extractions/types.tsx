export interface ExtractionTask {
  _id: string;
  site_id: string;
  doc_document_id: string;
  worker_id?: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: string;
  extraction_count?: number;
  header?: string[];
}

export interface ContentExtractionResult {
  _id: string;
  content_extraction_task_id: string;
  first_collected_date: string;
  result: {};
  translation?: {
    code?: string;
    name?: string;
    tier?: number;
    pa?: string;
    pan?: string;
    st?: string;
    stn?: string;
    ql?: string;
    qln?: string;
    sp?: string;
  };
  page: number;
  row: number;
}
