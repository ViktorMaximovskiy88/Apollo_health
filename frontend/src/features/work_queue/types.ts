import { BaseDocument } from '../types';

export interface SubmitAction {
  label: string;
  submit_action: any;
  primary: boolean;
}

export interface WorkQueue extends BaseDocument {
  name: string;
  document_query: any;
  user_query: any;
  submit_actions: SubmitAction[];
  disabled: boolean;
}

export interface WorkQueueCount {
  work_queue_id: string;
  count: number;
}