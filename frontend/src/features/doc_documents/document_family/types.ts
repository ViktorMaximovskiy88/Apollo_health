import { BaseDocument } from '../../../common';

export interface DocumentFamily extends BaseDocument {
  name: string;
  document_type: string;
  description: string;
  site_ids: string[];
  relevance: string[];
  disabled: boolean;
  legacy_relevance: string[];
  field_groups: string[];
}
