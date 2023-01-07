import { BaseDocument } from '../../common';

export interface DevToolsDoc extends BaseDocument {
  name: string;
  lineage_id: string;
  previous_doc_doc_id: string;
  retrieved_document_id: string;
  is_current_version: boolean;
  file_extension: string;
  checksum: string;
  document_type: string;
  final_effective_date: string;
}

export interface DevToolsGroup {
  lineageId: string;
  items: DevToolsDoc[];
  collapsed: boolean;
}
