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
  { id: 'Formulary Update', value: 'Formulary Update', label: 'Formulary Update' },
  { id: 'NCCN Guideline', value: 'NCCN Guideline', label: 'NCCN Guideline' },
  { id: 'Restriction List', value: 'Restriction List', label: 'Restriction List' },
  {
    id: 'Review Committee Meetings',
    value: 'Review Committee Meetings',
    label: 'Review Committee Meetings',
  },

  { id: 'Not Applicable', value: 'Not Applicable', label: 'Not Applicable' },
];
export const FieldGroupsOptions = [
  { id: 'AUTHORIZATION_DETAILS', label: 'Authorization Details', value: 'AUTHORIZATION_DETAILS' },
  { id: 'TIER', label: 'Tier', value: 'TIER' },
  { id: 'COVERAGE', label: 'Coverage', value: 'COVERAGE' },
  { id: 'QL_GATE', label: 'QL Gate', value: 'QL_GATE' },
  { id: 'QL_DETAILS', label: 'QL Details', value: 'QL_DETAILS' },
  { id: 'PA', label: 'PA', value: 'PA' },
  { id: 'ST', label: 'ST', value: 'ST' },
  { id: 'SP_GATE', label: 'SP Gate', value: 'SP_GATE' },
  { id: 'SP_DETAILS', label: 'SP Details', value: 'SP_DETAILS' },
  {
    id: 'TREATMENT_REQUEST_FORM',
    label: 'Treatment Request Form',
    value: 'TREATMENT_REQUEST_FORM',
  },
  { id: 'COVERAGE_NOTES', label: 'Coverage Notes', value: 'COVERAGE_NOTES' },
  { id: 'SITE_OF_CARE', label: 'Site of Care', value: 'SITE_OF_CARE' },
];

export const LegacyRelevanceOptions = [
  { id: 'EDITOR_MANUAL', label: 'Editor Manual', value: 'EDITOR_MANUAL' },
  { id: 'EDITOR_AUTOMATED', label: 'Editor Automated ', value: 'EDITOR_AUTOMATED' },
  { id: 'PAR', label: 'PAR', value: 'PAR' },
  { id: 'N/A', label: 'N/A', value: 'N/A' },
];

export const languageCodes = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'other', label: 'Other' },
];
