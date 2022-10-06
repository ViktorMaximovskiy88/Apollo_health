import { BaseDocument } from '../../common';

export interface LineageDoc extends BaseDocument {
  name: string;
  lineage_id: string;
  previous_doc_id: string;
  retrieved_doc_id: string;
  is_current_version: boolean;
  file_extension: string;
  checksum: string;
  document_type: string;
  final_effective_date: string;
}

export interface LineageGroup {
  lineageId: string;
  items: LineageDoc[];
  collapsed: boolean;
}
