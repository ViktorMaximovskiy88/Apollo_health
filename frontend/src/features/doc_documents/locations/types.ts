import { PayerFamily } from '../../payer-family/types';

export interface DocDocumentLocation {
  base_url: string;
  url: string;
  link_text: string;
  closest_heading: string;
  site_id: string;
  site_name?: string;
  first_collected_date: string;
  last_collected_date: string;
  previous_doc_doc_id: string;
  payer_family_id: string;
  payer_family: PayerFamily;
}
