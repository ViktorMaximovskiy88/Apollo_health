import { BaseDocument } from '../../common/types';

export interface DocumentQuery {
  scrape_task_id?: string | null;
  site_id?: string | null;
  logical_document_id?: string | null;
  translation_id?: boolean;
}

export interface RetrievedDocument extends BaseDocument {
  _id: string;
  site_id: string;
  scrape_task_id: string;
  logical_document_id?: string;
  logical_document_version?: number;
  document_type?: string;
  doc_type_confidence?: number;
  first_collected_date: string;
  last_collected_date: string;
  internal_document: boolean;
  disabled: boolean;
  url: string;
  checksum: string;
  name?: string;
  metadata?: { [key: string]: string };
  context_metadata?: { [key: string]: string };
  effective_date?: string;
  end_date?: string;
  last_updated_date?: string;
  last_reviewed_date?: string;
  next_review_date?: string;
  next_update_date?: string;
  published_date?: string;
  identified_dates?: string[];
  base_url: string;
  lang_code: string;
  file_extension: string;
}

// id is added so that it can be used for both table filters and dropdown selections
export const DocumentTypes = [
  { id: 'Authorization Policy', value: 'Authorization Policy', label: 'Authorization Policy' },
  { id: 'Provider Guide', value: 'Provider Guide', label: 'Provider Guide' },
  {
    id: 'Treatment Request Form',
    value: 'Treatment Request Form',
    label: 'Treatment Request Form',
  },
  { id: 'Payer Unlisted Policy', value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
  {
    id: 'Covered Treatment List',
    value: 'Covered Treatment List',
    label: 'Covered Treatment List',
  },
  { id: 'Regulatory Document', value: 'Regulatory Document', label: 'Regulatory Document' },
  { id: 'Formulary', value: 'Formulary', label: 'Formulary' },
  { id: 'Internal Reference', value: 'Internal Reference', label: 'Internal Reference' },
  { id: 'Not Applicable', value: 'Not Applicable', label: 'Not Applicable' },
];

export const languageCodes = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'other', label: 'Other' },
];
