/* API client for AdeshX backend */

import axios from 'axios';
import type {
  Document, DocumentListResponse, ExtractedData,
  ActionPlan, ActionPlanListResponse, Verification,
  DashboardSummary, DashboardCasesResponse, UpcomingDeadline
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ── Documents ────────────────────────────────────────────────────

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<Document>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const { data } = await api.get<DocumentListResponse>('/documents/');
  return data;
}

export async function getDocument(id: string): Promise<Document> {
  const { data } = await api.get<Document>(`/documents/${id}`);
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/documents/${id}`);
}

export function getPdfUrl(id: string): string {
  return `/api/documents/${id}/pdf`;
}

// ── Extraction ───────────────────────────────────────────────────

export async function triggerExtraction(documentId: string): Promise<ExtractedData> {
  const { data } = await api.post<ExtractedData>(`/extraction/${documentId}/extract`);
  return data;
}

export async function getExtraction(documentId: string): Promise<ExtractedData> {
  const { data } = await api.get<ExtractedData>(`/extraction/${documentId}`);
  return data;
}

// ── Action Plans ─────────────────────────────────────────────────

export async function generateActionPlan(documentId: string): Promise<ActionPlan> {
  const { data } = await api.post<ActionPlan>(`/actions/${documentId}/generate`);
  return data;
}

export async function getActionPlans(documentId: string): Promise<ActionPlanListResponse> {
  const { data } = await api.get<ActionPlanListResponse>(`/actions/${documentId}`);
  return data;
}

// ── Verification ─────────────────────────────────────────────────

export async function submitVerification(
  documentId: string,
  status: string,
  edits: Record<string, any> = {},
  notes: string = ''
): Promise<Verification> {
  const { data } = await api.put<Verification>(`/actions/${documentId}/verify`, {
    status, edits, notes, verified_by: 'admin',
  });
  return data;
}

export async function getVerification(documentId: string): Promise<Verification> {
  const { data } = await api.get<Verification>(`/actions/${documentId}/verification`);
  return data;
}

// ── Dashboard ────────────────────────────────────────────────────

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>('/dashboard/summary');
  return data;
}

export async function getDashboardCases(
  filters?: { department?: string; priority?: string; action_type?: string }
): Promise<DashboardCasesResponse> {
  const { data } = await api.get<DashboardCasesResponse>('/dashboard/cases', { params: filters });
  return data;
}

export async function getDeadlines(): Promise<UpcomingDeadline[]> {
  const { data } = await api.get<UpcomingDeadline[]>('/dashboard/deadlines');
  return data;
}
