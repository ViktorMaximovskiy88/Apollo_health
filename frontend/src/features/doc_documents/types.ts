import { BaseDocument, TaskStatus } from "../../common";

export interface TherapyTag {
    text: string;
    page: number;
    code: string;
    score: number;
    relevancy: number;
}

export interface IndicationTag {
    text: string;
    page: number;
    code: string;
    score: number;
    relevancy: number;
}

export interface TaskLock {
    work_queue_id: string;
    user_id: string;
    expires: string;
}

export interface DocDocument extends BaseDocument {
    site_id: string
    retrieved_document_id: string
    classification_status: TaskStatus
    classification_lock: TaskLock
    name: string
    checksum: string
    document_type: string
    doc_type_confidence: number

    effective_date: string
    last_reviewed_date: string
    last_updated_date: string
    next_review_date: string
    next_update_date: string
    first_created_date: string
    published_date: string

    final_effective_date: string
    end_date: string

    first_collected_date: string
    last_collected_date: string

    lineage_id: string
    version: string
    
    url: string
    base_url: string
    link_text: string

    lang_code: string
    
    therapy_tags: TherapyTag[]
    indication_tags: IndicationTag[]
    
    automated_content_extraction: boolean
    automated_content_extraction_class: string
    
    tags: string[]
}