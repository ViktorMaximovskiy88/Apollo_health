import { BaseDocument } from '../../common';
import { DocPipelineStages } from '../../common/types';
import { ApprovalStatus } from '../../common/approvalStatus';
import { DocDocumentLocation } from './locations/types';

export enum TagUpdateStatus {
  Changed = 'CHANGED',
  Added = 'ADDED',
  Removed = 'REMOVED',
}
export interface BaseDocTag {
  id: string;
  _type: 'indication' | 'therapy';
  _normalized: string;
}

export interface TherapyTag {
  name: string;
  text: string;
  page: number;
  code: string;
  score: number;
  focus: boolean;
  priority: number;
  update_status?: TagUpdateStatus;
  text_area?: [number, number];
  created_at?: string;
}

export interface IndicationTag {
  name?: string;
  text: string;
  page: number;
  code: number;
  focus?: boolean; // migrate and update
  priority: number;
  update_status?: TagUpdateStatus;
  text_area?: [number, number];
}

export interface DocumentSection {
  key_text: string;
  section_status?: TagUpdateStatus;
  current_page?: number | null;
  prev_page?: number | null;
}

export interface TagComparison {
  current_doc_id: string;
  prev_doc_id: string;
  therapy_tag_sections: DocumentSection[];
  indication_tag_sections: DocumentSection[];
}

export enum TagType {
  Indication = 'indication',
  Therapy = 'therapy',
}

export interface UIIndicationTag extends IndicationTag, BaseDocTag {}
export interface UITherapyTag extends TherapyTag, BaseDocTag {}
export type DocumentTag = UIIndicationTag | UITherapyTag;

export interface TaskLock {
  work_queue_id: string;
  user_id: string;
  expires: string;
}

export interface CompareRequest {
  current_id?: string;
  prev_id?: string;
}

export interface CompareResponse extends BaseDocument {
  exists: boolean;
  pending: boolean;
  new_key?: string;
  prev_key?: string;
  tag_comparison?: TagComparison;
}

export interface DocDocument extends BaseDocument {
  retrieved_document_id: string;
  classification_status: ApprovalStatus;
  family_status: ApprovalStatus;
  content_extraction_status: ApprovalStatus;
  status: ApprovalStatus;
  classification_hold_info: string[];
  extraction_hold_info: string[];
  family_hold_info: string[];
  classification_lock: TaskLock;
  name: string;
  checksum: string;
  file_extension: string;

  document_type: string;
  doc_type_confidence: number;

  document_family_id?: string | null;
  document_family?: any;

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
  is_current_version: boolean;
  version: string;
  internal_document: boolean;
  previous_doc_doc_id: string | null;

  locations: DocDocumentLocation[];

  lang_code: string;

  therapy_tags: TherapyTag[];
  indication_tags: IndicationTag[];

  translation_id?: string;
  content_extraction_task_id?: string;

  tags: string[];

  pipeline_stages: DocPipelineStages;

  include_later_documents_in_lineage_update?: boolean;
  priority: number;
  previous_par_id: string | null;

  hold_type?: string;
}

export type SiteDocDocument = Omit<
  DocDocument,
  'locations' | 'first_collected_date' | 'last_collected_date'
> &
  DocDocumentLocation;

export interface DocBulkUpdateResponse {
  count_success: number;
  count_error: number;
  errors: string[];
}
