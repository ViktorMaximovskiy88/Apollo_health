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
  is_current_version: boolean;
}

// id is added so that it can be used for both table filters and dropdown selections
export const DocumentTypes = [
  {
    id: 'Annual Notice of Changes',
    label: 'Annual Notice of Changes',
    value: 'Annual Notice of Changes',
  },
  { id: 'Authorization Policy', label: 'Authorization Policy', value: 'Authorization Policy' },
  { id: 'Directory', label: 'Directory', value: 'Directory' },
  { id: 'Evidence of Coverage', label: 'Evidence of Coverage', value: 'Evidence of Coverage' },
  { id: 'Exclusion List', label: 'Exclusion List', value: 'Exclusion List' },
  { id: 'Fee Schedule', label: 'Fee Schedule', value: 'Fee Schedule' },
  { id: 'Formulary Update', label: 'Formulary Update', value: 'Formulary Update' },
  { id: 'Formulary', label: 'Formulary', value: 'Formulary' },
  { id: 'Internal Resource', label: 'Internal Resource', value: 'Internal Resource' },
  { id: 'LCD', label: 'LCD', value: 'LCD' },
  { id: 'Medical Coverage List', label: 'Medical Coverage List', value: 'Medical Coverage List' },
  { id: 'NCCN Guideline', label: 'NCCN Guideline', value: 'NCCN Guideline' },
  { id: 'NCD', label: 'NCD', value: 'NCD' },
  { id: 'New-to-Market Policy', label: 'New-to-Market Policy', value: 'New-to-Market Policy' },
  {
    id: 'Newsletter / Announcement',
    label: 'Newsletter / Announcement',
    value: 'Newsletter / Announcement',
  },
  { id: 'Not Applicable', label: 'Not Applicable', value: 'Not Applicable' },
  { id: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy', value: 'Payer Unlisted Policy' },
  { id: 'Preventive Drug List', label: 'Preventive Drug List', value: 'Preventive Drug List' },
  { id: 'Provider Guide', label: 'Provider Guide', value: 'Provider Guide' },
  { id: 'Regulatory Document', label: 'Regulatory Document', value: 'Regulatory Document' },
  { id: 'Restriction List', label: 'Restriction List', value: 'Restriction List' },
  { id: 'Site of Care Policy', label: 'Site of Care Policy', value: 'Site of Care Policy' },
  { id: 'Specialty List', label: 'Specialty List', value: 'Specialty List' },
  { id: 'Summary of Benefits', label: 'Summary of Benefits', value: 'Summary of Benefits' },
  {
    id: 'Review Committee Meetings',
    label: 'Review Committee Meetings',
    value: 'Review Committee Meetings',
  },
  {
    id: 'Review Committee Schedule',
    label: 'Review Committee Schedule',
    value: 'Review Committee Schedule',
  },
  {
    id: 'Treatment Request Form',
    label: 'Treatment Request Form',
    value: 'Treatment Request Form',
  },
];

export const documentTypes = DocumentTypes;

export const languageCodes = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'other', label: 'Other' },
];
