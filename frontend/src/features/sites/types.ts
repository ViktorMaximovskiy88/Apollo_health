import { BaseDocument, TaskStatus } from '../../common';

export interface BaseUrl {
  url: string;
  name: string;
  status: string;
}

export interface Site extends BaseDocument {
  name: string;
  base_urls: BaseUrl[];
  scrape_method: string;
  collection_method: string;
  scrape_method_configuration: {
    document_extensions: string[];
    url_keywords: string[];
    proxy_exclusions: string[];
    wait_for: string[];
    follow_links: boolean;
    follow_link_keywords: string[];
    follow_link_url_keywords: string[];
  };
  tags: string[];
  disabled: boolean;
  last_run_time?: string;
  last_run_status: TaskStatus;
  cron: string;
  playbook?: string;
  status: string;
}

export interface Proxy extends BaseDocument {
  name: string;
}

export interface ActiveUrlResponse {
  in_use: boolean;
  site?: Site;
}

export enum CollectionMethod {
  Automated = 'AUTOMATED',
  Manual = 'MANUAL',
}
