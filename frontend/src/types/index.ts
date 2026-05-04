/* TypeScript types matching backend Pydantic schemas */

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  page_count: number;
  status: string;
  upload_date: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface ExtractedField<T = string> {
  value: T;
  source_text: string;
  page_number: number;
  confidence: number;
}

export interface ExtractedData {
  id: string;
  document_id: string;
  case_title: ExtractedField;
  case_number: ExtractedField;
  parties_involved: ExtractedField<{ name: string; role: string }>[];
  date_of_order: ExtractedField;
  judge_name: ExtractedField;
  court_name: ExtractedField;
  key_directives: ExtractedField<string>[];
  deadlines: ExtractedField<{ description: string; date: string }>[];
  responsible_authority: ExtractedField;
  validation_flags: { rule: string; message: string; severity: "error" | "warning" }[];
  extraction_metadata: Record<string, any>;
  confidence_scores: Record<string, number>;
  created_at: string;
}

export interface ActionPlan {
  id: string;
  document_id: string;
  action_required: string;
  reasoning: string;
  deadline: string;
  deadline_date: string | null;
  responsible_department: string;
  priority: string;
  confidence_score: number;
  risk_score: number;
  source_text: string;
  page_number: number | null;
  auto_deadlines: { type: string; days: number; calculated_date: string; source: string }[];
  created_at: string;
}

export interface ActionPlanListResponse {
  action_plans: ActionPlan[];
}

export interface Verification {
  id: string;
  document_id: string;
  status: string;
  verified_by: string;
  edits: Record<string, any>;
  notes: string;
  verified_at: string | null;
}

export interface DashboardSummary {
  total_documents: number;
  pending_verification: number;
  verified: number;
  rejected: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
  departments: { department: string; count: number }[];
}

export interface DashboardCase {
  document_id: string;
  case_title: string;
  case_number: string;
  date_of_order: string;
  action_required: string;
  priority: string;
  deadline: string;
  deadline_date: string | null;
  responsible_department: string;
  confidence_score: number;
  risk_score: number;
  verified_at: string | null;
  status: string;
}

export interface DashboardCasesResponse {
  cases: DashboardCase[];
  total: number;
}

export interface UpcomingDeadline {
  document_id: string;
  case_title: string;
  action_required: string;
  deadline: string;
  deadline_date: string | null;
  responsible_department: string;
  priority: string;
  days_remaining: number | null;
}
