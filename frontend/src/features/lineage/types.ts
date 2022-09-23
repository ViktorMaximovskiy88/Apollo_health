import { BaseDocument } from '../../common';

export interface LineageDoc extends BaseDocument {
  name: string;
  lineage_id: string;
  previous_doc_id: string;
  is_current_version: boolean;
  file_extension: string;
  checksum: string;
}

export interface LineageGroup {
  lineageId: string;
  items: LineageDoc[];
}
