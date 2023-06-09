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

export interface FocusSectionConfig {
  doc_type: string;
  section_type: SectionType[];
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
    scrape_base_page: boolean;
    searchable: boolean;
    search_prefix_length: number | null;
    searchable_type: SearchableType[];
    searchable_input: AttrSelector | null;
    searchable_submit: AttrSelector | null;
    searchable_playbook: string | null;
    attr_selectors: AttrSelector[];
    html_attr_selectors: AttrSelector[];
    html_exclusion_selectors: AttrSelector[];
    focus_section_configs: FocusSectionConfig[];
    cms_doc_types: CmsDocType[];
    debug: boolean;
  };
  tags: string[];
  disabled: boolean;
  last_run_time?: string;
  last_run_status: TaskStatus;
  cron: string;
  playbook?: string;
  status: string;
  assignee?: string;
  doc_type_threshold_override: boolean;
  doc_type_threshold: number;
  lineage_threshold_override: boolean;
  lineage_threshold: number;
  additional_languages: string[];
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

export const collectionMethodOptions = [
  { id: CollectionMethod.Automated, label: 'Automated' },
  { id: CollectionMethod.Manual, label: 'Manual' },
];

export function collectMethodDisplayName(method: string) {
  return collectionMethodOptions.find(({ id }) => id === method)?.label;
}

export enum ScrapeMethod {
  Simple = 'SimpleDocumentScrape',
  Html = 'HtmlScrape',
  CMS = 'CMSScrape',
  Tricare = 'TricareScrape',
}

export enum SearchableType {
  CPTCodes = 'CPTCODES',
  JCodes = 'JCODES',
  Universal = 'UNIVERSAL',
}

export enum SectionType {
  Therapy = 'THERAPY',
  Indication = 'INDICATION',
  Key = 'KEY',
}

export enum CmsDocType {
  NCD = 1,
  LCD = 2,
  LCA = 3,
}
