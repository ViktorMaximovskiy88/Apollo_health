import { BaseDocument } from '../types';

export enum Status {
  Failed = 'FAILED',
  Canceled = 'CANCELED',
  Canceling = 'CANCELING',
  InProgress = 'IN_PROGRESS',
  Queued = 'QUEUED',
  Finished = 'FINISHED',
}

export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: Status;
  documents_found: number;
  links_found: number;
  new_ldocuments_found: number;
}
