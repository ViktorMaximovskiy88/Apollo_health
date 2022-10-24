import { BaseDocument } from '../../common';

export interface Comment extends BaseDocument {
  time: string;
  target_id: string;
  user_id: string;
  text: string;
}
