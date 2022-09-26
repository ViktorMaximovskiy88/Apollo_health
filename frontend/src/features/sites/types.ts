import { BaseDocument, TaskStatus } from '../../common';

export interface BaseUrl {
  url: string;
  name: string;
  status: string;
}

export interface AttrSelector {
  attr_element: string;
  attr_name: string;
  attr_value?: string;
  has_text?: string;
  resource_address: boolean;
}

export interface FocusTherapyConfig {
  doc_type: string;
  start_separator: string;
  end_separator: string;
  all_focus: boolean;
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
    searchable: boolean;
    searchable_type: SearchableType | null;
    searchable_input: AttrSelector | null;
    searchable_submit: AttrSelector | null;
    attr_selectors: AttrSelector[];
    html_attr_selectors: AttrSelector[];
    html_exclusion_selectors: AttrSelector[];
    focus_therapy_configs: FocusTherapyConfig[];
    allow_docdoc_updates: boolean;
  };
  tags: string[];
  disabled: boolean;
  last_run_time?: string;
  last_run_status: TaskStatus;
  cron: string;
  playbook?: string;
  status: string;
  assignee?: string;
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

export enum ScrapeMethod {
  Simple = 'SimpleDocumentScrape',
  Html = 'HtmlScrape',
}

export enum SearchableType {
  CPTCodes = 'CPTCODES',
  JCodes = 'JCODES',
}
