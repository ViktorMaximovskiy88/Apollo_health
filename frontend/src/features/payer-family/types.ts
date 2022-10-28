import { BaseDocument } from '../../common';

export interface PayerFamily extends BaseDocument {
  name: string;
  document_type: string;
  payer_type: string;
  payer_ids: string[];
  channels: string[];
  benefits: string[];
  plan_types: string[];
  regions: string[];
  auto_generated: boolean;
}
