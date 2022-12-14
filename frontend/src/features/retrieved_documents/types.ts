import { BaseDocument } from '../../common/types';

export interface DocumentQuery {
  scrape_task_id?: string | null;
  site_id?: string | null;
  logical_document_id?: string | null;
  translation_id?: boolean;
}

export interface PipelineStage {
  version: number;
  version_at: string;
  is_locked: boolean;
}

export interface DocPipelineStages {
  content: PipelineStage | undefined;
  date: PipelineStage | undefined;
  doc_type: PipelineStage | undefined;
  tag: PipelineStage | undefined;
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
  pipeline_stages: DocPipelineStages;
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
  { id: 'Internal Reference', label: 'Internal Reference', value: 'Internal Reference' },
  { id: 'LCD', label: 'LCD', value: 'LCD' },
  { id: 'Medical Coverage List', label: 'Medical Coverage List', value: 'Medical Coverage List' },
  { id: 'Member Resources', label: 'Member Resources', value: 'Member Resources' },
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
    id: 'Treatment Request Form',
    label: 'Treatment Request Form',
    value: 'Treatment Request Form',
  },
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

export const documentTypes = DocumentTypes;

export const languageCodes = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'other', label: 'Other' },
];

export const getFieldGroupLabel = (id: string) => {
  return FieldGroupsOptions.find((e) => {
    return e.id === id;
  })?.label;
};
export const getLegacyRelevanceLable = (id: string) => {
  return LegacyRelevanceOptions.find((e) => {
    return e.id === id;
  })?.label;
};
