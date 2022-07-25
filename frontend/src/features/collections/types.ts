import { BaseDocument, TaskStatus } from '../../common';

export interface SiteScrapeTask extends BaseDocument {
  site_id: string;
  queued_time: string;
  start_time?: string;
  end_time?: string;
  status: TaskStatus;
  links_found: number;
  error_message?: string | null;
  documents_found: number;
  new_documents_found: number;
  collection_type: string;
}


export const documentTypes = [
  { value: 'Authorization Policy', label: 'Authorization Policy' },
  { value: 'Provider Guide', label: 'Provider Guide' },
  { value: 'Treatment Request Form', label: 'Treatment Request Form' },
  { value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
  { value: 'Covered Treatment List', label: 'Covered Treatment List' },
  { value: 'Regulatory Document', label: 'Regulatory Document' },
  { value: 'Formulary', label: 'Formulary' },
  { value: 'Internal Reference', label: 'Internal Reference' },
];