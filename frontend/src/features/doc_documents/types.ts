import { BaseDocument } from '../../common';
import { ApprovalStatus } from '../../common/approvalStatus';
import { RetrievedDocument } from '../retrieved_documents/types';

export interface BaseDocTag {
  id: string;
  _type: 'indication' | 'therapy' | 'therapy-group';
  _normalized: string;
}

export interface DocDocumentLocation {
  base_url: string;
  url: string;
  link_text: string;
  closest_heading: string;
  site_id: string;
  first_collected_date: string;
  last_collected_date: string;
  previous_doc_doc_id: string;
}

export interface TherapyTag extends BaseDocTag {
  name: string;
  text: string;
  page: number;
  code: string;
  score: number;
  focus: boolean;
}

export interface IndicationTag extends BaseDocTag {
  name?: string;
  text: string;
  page: number;
  code: string;
}

export interface TaskLock {
  work_queue_id: string;
  user_id: string;
  expires: string;
}

export interface CompareRequest extends BaseDocument {
  compareId?: string;
}

export interface CompareResponse extends BaseDocument {
  diff: string;
  org_doc: DocDocument;
  new_doc: RetrievedDocument;
}

export interface DocDocument extends BaseDocument {
  retrieved_document_id: string;
  classification_status: ApprovalStatus;
  classification_lock: TaskLock;
  name: string;
  checksum: string;
  file_extension: string;

  document_type: string;
  doc_type_confidence: number;

  document_family_id?: string;

  effective_date: string;
  last_reviewed_date: string;
  last_updated_date: string;
  next_review_date: string;
  next_update_date: string;
  first_created_date: string;
  published_date: string;
  identified_dates: string[];

  final_effective_date: string;
  end_date: string;

  first_collected_date: string;
  last_collected_date: string;

  lineage_id: string;
  version: string;

  locations: DocDocumentLocation[];

  lang_code: string;

  therapy_tags: TherapyTag[];
  indication_tags: IndicationTag[];

  translation_id?: string;

  tags: string[];
}

export type SiteDocDocument = Omit<
  DocDocument,
  'locations' | 'first_collected_date' | 'last_collected_date'
> &
  DocDocumentLocation;

export interface DocumentFamilyType extends BaseDocument {
  name: string;
  document_type: string;
  description: string;
  site_id: string;
  relevance: string[];
}

export interface DocumentFamilyOption {
  label: string;
  value: string | null;
}
