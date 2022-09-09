import { BaseDocument, TaskStatus } from '../../common';

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
