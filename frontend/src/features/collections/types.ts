import { BaseDocument, TaskStatus } from '../../common';

export enum WorkItemOption {
  Found = 'FOUND',
  NewDocument = 'NEW_DOCUMENT',
  NewVersion = 'NEW_VERSION',
  NotFound = 'NOT_FOUND',
  Unhandled = 'UNHANDLED',
}
export interface WorkItem {
  document_id: string;
  selected: WorkItemOption;
  new_doc?: string;
  prev_doc?: string;
  action_datetime?: string;
}
export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: TaskStatus;
  links_found: number;
  error_message?: string | null;
  documents_found: number;
  new_documents_found: number;
  collection_method: string;
  work_list: WorkItem[];
}

export enum BulkActionTypes {
  Cancel = 'CANCEL',
  CancelHold = 'CANCEL-HOLD',
  Hold = 'HOLD',
  Run = 'RUN',
}

export interface CollectionConfig {
  defaultLastNDays: number;
}
