import { BaseDocument } from '../types';

export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: string;
  links_found: number;
  documents_found: number;  
  new_ldocuments_found: number;
}
