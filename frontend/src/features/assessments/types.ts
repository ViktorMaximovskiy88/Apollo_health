import { BaseDocument } from '../types';

export interface AssessmentLock {
  work_queue_id: string;
  user_id: string;
  expires: string;
}

export interface Comment {
  user_id: string;
  time: string;
  comment: string;
}

export interface Triage {
  effective_date: string;
  document_type: string;
  document_lineage_id: string;
  comments: Comment[];
};

export interface DocumentAssessment extends BaseDocument {
  name: string;
  analysis_status: string;
  triage_status: string;
  site_id: string;
  retrieved_document_id: string;
  triage: Triage;
  locks: AssessmentLock[];
}

export interface TakeDocumentAssessmentResponse {
  acquired_lock: boolean;
  lock?: AssessmentLock;
}