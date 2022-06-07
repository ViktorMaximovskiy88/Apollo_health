import { BaseDocument } from '../types';

export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status:
    | 'FAILED'
    | 'CANCELED'
    | 'CANCELING'
    | 'IN_PROGRESS'
    | 'QUEUED'
    | 'FINISHED';
  documents_found: number;
  links_found: number;
  new_ldocuments_found: number;
}
