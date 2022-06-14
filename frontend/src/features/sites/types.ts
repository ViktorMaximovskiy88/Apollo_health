import { BaseDocument } from '../types';

export interface BaseUrl {
  url: string;
  name: string;
  status: string;
}

export interface Site extends BaseDocument {
  name: string;
  base_urls: BaseUrl[];
  scrape_method: string;
  scrape_method_configuration: {
    document_extensions: string[];
    url_keywords: string[];
    proxy_exclusions: string[];
  };
  tags: string[];
  disabled: boolean;
  last_run_time?: string;
  last_status: string;
  cron: string;
}

export interface Proxy extends BaseDocument {
  name: string;
}

export interface ActiveUrlResponse {
  in_use: boolean;
  site?: Site;
}
