import { BaseDocument } from '../../common';

export interface WorkItemLock {
  work_queue_id: string;
  user_id: string;
  expires: string;
}

export interface SubmitAction {
  label: string;
  submit_action: {
    classification_status?: string;
    family_status?: string;
    content_extraction_status?: string;
  };
  primary: boolean;
  reassignable: boolean;
  require_comment: boolean;
  hold_types?: string[];
}

export interface WorkQueue extends BaseDocument {
  name: string;
  document_query: any;
  user_query: any;
  submit_actions: SubmitAction[];
  hold_types: string[];
  frontend_component: string;
  disabled: boolean;
}

export interface WorkQueueCount {
  work_queue_id: string;
  count: number;
}

export interface TakeWorkItemResponse {
  acquired_lock: boolean;
  lock?: WorkItemLock;
}

export interface TakeNextWorkItemResponse {
  acquired_lock: boolean;
  item_id: string;
}

export interface SubmitWorkItemResponse {
  success: boolean;
}

export interface SubmitWorkItemRequest {
  updates: any;
  action_label?: string;
  reassignment?: string;
  comment?: string;
  type?: string;
}
