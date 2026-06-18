export interface FieldExtraction {
    value: any;
    confidence: number;
    source_snippet: string | null;
}

export interface TradeDocumentExtraction {
    consignee_name: FieldExtraction;
    hs_code: FieldExtraction;
    port_of_loading: FieldExtraction;
    port_of_discharge: FieldExtraction;
    incoterms: FieldExtraction;
    description_of_goods: FieldExtraction;
    gross_weight: FieldExtraction;
    invoice_number: FieldExtraction;
    extraction_warnings?: string[];
}

export interface ValidationResult {
    result: 'match' | 'mismatch' | 'uncertain';
    expected_value: any;
    found_value: any;
    reason: string;
}

export interface PipelineRun {
    id: number;
    filename: string;
    upload_time: string;
    extracted_data: TradeDocumentExtraction;
    validation_results: Record<string, ValidationResult>;
    decision: 'auto_approve' | 'flag_review' | 'amendment_request';
    decision_reason: string;
    amendment_draft: string | null;
    status: 'pending_review' | 'approved' | 'amended';
    edited_data: TradeDocumentExtraction | null;
    logs?: string[];
}

export interface RuleDetail {
    type: string;
    expected?: any;
    expected_prefixes?: string[];
    expected_max?: number;
    expected_pattern?: string;
}

export interface RulesResponse {
    customer_name: string;
    rules: Record<string, RuleDetail>;
}

export interface AnalyticsResponse {
    total_runs: number;
    decisions: {
        auto_approve: number;
        flag_review: number;
        amendment_request: number;
    };
    statuses: {
        pending_review: number;
        approved: number;
        amended: number;
    };
}

export interface QueryResponse {
    success: boolean;
    sql: string | null;
    results: any[] | null;
    answer: string;
    error?: string;
}
