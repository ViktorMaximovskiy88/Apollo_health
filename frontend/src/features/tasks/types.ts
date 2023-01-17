import { BaseDocument } from '../../common';

export interface DocTask {
  doc_doc_id: string | undefined;
  reprocess: boolean;
}

export interface SiteTask {
  site_id: string | undefined;
  reprocess: boolean;
}

export interface EnqueueTask {
  task_type: string;
  payload: DocTask | SiteTask;
}

export interface Task extends BaseDocument {
  task_type: string;
  status: string;
  status_at: string;
  is_complete: boolean;
  completed_at: string;
  result?: { [key: string]: any };
}
