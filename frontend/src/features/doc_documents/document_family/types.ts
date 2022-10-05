import { BaseDocument } from '../../../common';

export interface PayerInfo {
  payer_type: string;
  payer_ids: string[];
  channels: string[];
  benefits: string[];
  plan_types: string[];
  regions: string[];
}

export interface DocumentFamily extends BaseDocument {
  name: string;
  document_type: string;
  description: string;
  site_id: string;
  relevance: string[];
  payer: PayerInfo;
}
