import { BaseDocument } from '../types';

export interface Site extends BaseDocument {
  name: string;
  base_url: string;
  scrape_method: string;
  tags: string[];
  disabled: boolean;
  last_status: string;
  cron: string;
}
