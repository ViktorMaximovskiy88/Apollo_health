import { BaseDocument, Status } from '../types';

export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: Status;
  documents_found: number;
  links_found: number;
  new_ldocuments_found: number;
  error_message: string;
}
