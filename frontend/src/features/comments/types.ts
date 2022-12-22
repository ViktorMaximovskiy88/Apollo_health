import { BaseDocument } from '../../common';

export interface Comment extends BaseDocument {
  time: string;
  target_id: string;
  user_id: string;
  text: string;
}

export enum CommentType {
  ClassificationHold = 'Classification Hold',
  DocPayerHold = 'Document and Payer Family Hold',
  TranslationConfigHold = 'Translation Config Hold',
}
