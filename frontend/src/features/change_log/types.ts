import { BaseDocument } from '../types';

export interface Patch {
  op: string;
  path: string;
  value?: string;
  prev?: string;
  from?: string;
}

export interface ChangeLog extends BaseDocument {
  user_id: string;
  target_id: string;
  collection: string;
  action: string;
  time: string;
  delta?: Patch[];
}
