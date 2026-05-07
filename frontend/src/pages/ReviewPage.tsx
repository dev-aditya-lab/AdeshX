import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Loader2, CheckCircle, XCircle, AlertTriangle, FileText,
  Play, Sparkles, ChevronLeft, Clock, Users, Gavel, Building2, Target
} from 'lucide-react';
import {
  getDocument, triggerExtraction, getExtraction,
  generateActionPlan, getActionPlans, submitVerification, getPdfUrl,
} from '../services/api';
import type { Document as DocType, ExtractedData, ActionPlan, ExtractedField } from '../types';

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [doc, setDoc] = useState<DocType | null>(null);
  const [extracted, setExtracted] = useState<ExtractedData | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlan | null>(null);
  const [step, setStep] = useState<'loading' | 'uploaded' | 'extracting' | 'extracted' | 'generating' | 'review' | 'verified'>('loading');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  useEffect(() => { if (id) loadDocument(); }, [id]);

  const loadDocument = async () => {
    try {
      const d = await getDocument(id!);
      setDoc(d);
      if (d.status === 'verified' || d.status === 'rejected') {
        await loadExistingData(); setStep('verified');
      } else if (d.status === 'action_generated') {
        await loadExistingData(); setStep('review');
      } else if (d.status === 'extracted') {
        await loadExtraction(); setStep('extracted');
      } else { setStep('uploaded'); }
    } catch { setError('Document not found'); }
  };

  const loadExistingData = async () => {
    try { const ext = await getExtraction(id!); setExtracted(ext); } catch {}
    try { const plans = await getActionPlans(id!); if (plans.action_plans.length > 0) setActionPlan(plans.action_plans[0]); } catch {}
  };

  const loadExtraction = async () => {
    try { const ext = await getExtraction(id!); setExtracted(ext); } catch {}
  };

  const handleExtract = async () => {
    setStep('extracting'); setError('');
    try { const ext = await triggerExtraction(id!); setExtracted(ext); setStep('extracted'); }
    catch (err: any) { setError(err?.response?.data?.detail || 'Extraction failed'); setStep('uploaded'); }
  };

  const handleGeneratePlan = async () => {
    setStep('generating'); setError('');
    try { const plan = await generateActionPlan(id!); setActionPlan(plan); setStep('review'); }
    catch (err: any) { setError(err?.response?.data?.detail || 'Action plan generation failed'); setStep('extracted'); }
  };

  const handleVerify = async (status: 'approved' | 'rejected') => {
    try {
      await submitVerification(id!, status, {}, notes); setStep('verified');
      if (status === 'approved') { setDoc(prev => prev ? { ...prev, status: 'verified' } : prev); }
    } catch (err: any) { setError(err?.response?.data?.detail || 'Verification failed'); }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button className="btn-secondary !p-2.5" onClick={() => navigate('/documents')}><ChevronLeft size={18} /></button>
          <div>
            <h1 className="text-2xl font-bold text-surface-900">{extracted?.case_title?.value || doc?.original_filename || 'Document Review'}</h1>
            <p className="text-surface-500 text-sm mt-0.5">{doc?.original_filename}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {['Upload', 'Extract', 'Action Plan', 'Verify'].map((s, i) => {
            const stepMap = ['uploaded', 'extracted', 'review', 'verified'];
            const currentIdx = stepMap.indexOf(step === 'extracting' ? 'uploaded' : step === 'generating' ? 'extracted' : step);
            const done = i <= currentIdx;
            return (
              <div key={s} className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${done ? 'bg-primary-500 text-white shadow-sm shadow-primary-500/30' : 'bg-surface-200 text-surface-400'}`}>
                  {done ? '✓' : i + 1}
                </div>
                <span className={`text-xs ${done ? 'text-primary-600 font-medium' : 'text-surface-400'}`}>{s}</span>
                {i < 3 && <div className={`w-8 h-0.5 ${done ? 'bg-primary-500' : 'bg-surface-200'}`} />}
              </div>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 rounded-xl bg-red-50 border border-red-200 text-danger-600 text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {extracted?.validation_flags && extracted.validation_flags.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm flex flex-col gap-2">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle size={16} /> Validation Warnings
          </div>
          <ul className="list-disc list-inside space-y-1 ml-1 text-xs">
            {extracted.validation_flags.map((flag, idx) => (
              <li key={idx}><strong>{flag.rule}</strong>: {flag.message}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="glass-card overflow-hidden flex flex-col h-[calc(100vh-200px)]">
          <div className="px-5 py-3 border-b border-surface-200 flex items-center gap-2 shrink-0">
            <FileText size={16} className="text-primary-600" />
            <span className="text-sm font-semibold text-surface-700">Document Preview</span>
          </div>
          <div className="flex-1 bg-surface-100/50">
            {id && (<iframe src={getPdfUrl(id)} className="w-full h-full border-0" title="PDF Viewer" />)}
          </div>
        </div>

        <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-200px)] pr-1">
          {step === 'uploaded' && (
            <div className="glass-card p-8 text-center mt-20">
              <Play size={48} className="text-primary-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-surface-900 mb-2">Ready to Extract</h3>
              <p className="text-surface-500 text-sm mb-6">Run AI extraction to identify case details, directives, and deadlines.</p>
              <button className="btn-primary" onClick={handleExtract}><Sparkles size={16} /> Start AI Extraction</button>
            </div>
          )}

          {step === 'extracting' && (
            <div className="glass-card p-8 text-center mt-20">
              <Loader2 size={48} className="text-primary-500 mx-auto mb-4 animate-spin" />
              <h3 className="text-lg font-semibold text-surface-900 mb-2">Extracting Information...</h3>
              <p className="text-surface-500 text-sm">Running OCR + Hybrid NLP pipeline</p>
            </div>
          )}

          {(step === 'extracted' || step === 'generating' || step === 'review' || step === 'verified') && extracted && (
            <>
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-surface-600 uppercase tracking-wider mb-4">Extracted Information</h3>
                <div className="space-y-4">
                  <ExtractedFieldRow icon={Gavel} label="Case Title" field={extracted.case_title} />
                  <ExtractedFieldRow icon={FileText} label="Case Number" field={extracted.case_number} />
                  <ExtractedFieldRow icon={Clock} label="Date of Order" field={extracted.date_of_order} />
                  <ExtractedFieldRow icon={Users} label="Judge" field={extracted.judge_name} />
                  <ExtractedFieldRow icon={Building2} label="Court" field={extracted.court_name} />
                  
                  {extracted.parties_involved?.length > 0 && (
                    <div>
                      <span className="text-xs text-surface-500 uppercase tracking-wider">Parties</span>
                      <div className="mt-2 space-y-2">
                        {extracted.parties_involved.map((p, i) => (
                          <div key={i} className="p-2 rounded-md bg-surface-50 border border-surface-200 text-sm">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-surface-800">{p.value?.name || 'Unknown'}</span>
                              <span className="badge badge-info text-[10px]">{p.value?.role || 'Unknown'}</span>
                              <ConfidenceBadge score={p.confidence} />
                            </div>
                            {p.source_text && <p className="text-xs text-surface-500 italic mt-1 ml-2 border-l border-primary-200 pl-2 text-wrap">"{p.source_text}"</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {extracted.key_directives?.length > 0 && (
                <div className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-surface-600 uppercase tracking-wider mb-3"><Target size={14} className="inline mr-2" />Key Directives</h3>
                  <div className="space-y-3">
                    {extracted.key_directives.map((d, i) => (
                      <div key={i} className="p-3 rounded-lg bg-surface-50 border border-surface-200 relative group">
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <ConfidenceBadge score={d.confidence} />
                        </div>
                        <p className="text-sm text-surface-800 font-medium mb-1 pr-10">{d.value}</p>
                        {d.source_text && (
                            <p className="text-xs text-surface-500 italic border-l-2 border-primary-300 pl-2 py-0.5 mt-2 bg-surface-100 rounded-r">
                                "{d.source_text}" <span className="text-primary-500 font-medium ml-1">(Page {d.page_number || '?'})</span>
                            </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {step === 'extracted' && (
                <button className="btn-primary w-full justify-center py-3" onClick={handleGeneratePlan}><Sparkles size={16} /> Generate Action Plan</button>
              )}
              
              {step === 'generating' && (
                <div className="glass-card p-6 text-center">
                  <Loader2 size={32} className="text-primary-500 mx-auto mb-3 animate-spin" />
                  <p className="text-surface-600 text-sm">Generating action plan from directives...</p>
                </div>
              )}
            </>
          )}

          {(step === 'review' || step === 'verified') && actionPlan && (
            <div className="glass-card p-5 border-2 border-primary-100">
              <h3 className="text-sm font-bold text-primary-700 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Sparkles size={16} /> Proposed Action Plan
              </h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className={`badge ${actionPlan.priority === 'high' ? 'badge-high' : actionPlan.priority === 'medium' ? 'badge-medium' : 'badge-low'}`}>{actionPlan.priority.toUpperCase()} PRIORITY</span>
                  <span className="badge badge-info">{actionPlan.action_required.toUpperCase()}</span>
                </div>
                
                <div>
                  <span className="text-xs text-surface-500 uppercase tracking-wider flex items-center gap-1.5"><Building2 size={12} /> Department</span>
                  <p className="text-sm text-surface-800 mt-0.5 font-semibold">{actionPlan.responsible_department}</p>
                </div>
                
                <div>
                  <span className="text-xs text-surface-500 uppercase tracking-wider flex items-center gap-1.5"><Clock size={12} /> Deadline</span>
                  <p className="text-sm text-surface-800 mt-0.5 font-semibold">{actionPlan.deadline}</p>
                </div>
                
                <div>
                  <span className="text-xs text-surface-500 uppercase tracking-wider">Reasoning</span>
                  <p className="text-sm text-surface-700 mt-1 leading-relaxed">{actionPlan.reasoning}</p>
                </div>
                
                {actionPlan.source_text && (
                  <div>
                    <span className="text-xs text-surface-500 uppercase tracking-wider">Source Text Reference</span>
                    <p className="text-xs text-surface-500 mt-1 italic border-l-2 border-primary-300 pl-3 py-1 bg-surface-50 rounded-r">"{actionPlan.source_text}"</p>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-3 mt-2">
                  <div className="p-3 rounded-lg bg-primary-50 border border-primary-100 text-center">
                    <p className="text-xs text-primary-600/70 font-semibold uppercase tracking-wider">Plan Confidence</p>
                    <p className="text-xl font-bold text-primary-700">{(actionPlan.confidence_score * 100).toFixed(0)}%</p>
                  </div>
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-100 text-center">
                    <p className="text-xs text-amber-600/70 font-semibold uppercase tracking-wider">Risk Score</p>
                    <p className="text-xl font-bold text-amber-700">{(actionPlan.risk_score * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>

              {step === 'review' && (
                <div className="mt-6 pt-5 border-t border-surface-200">
                  <label className="text-xs font-semibold text-surface-700 uppercase tracking-wider mb-2 block">Verification Notes (optional)</label>
                  <textarea value={notes} onChange={(e) => setNotes(e.target.value)} className="input-field mb-4 h-20 resize-none text-sm" placeholder="Add notes or required edits before approval..." />
                  <div className="flex gap-3">
                    <button className="btn-primary flex-1 justify-center py-2.5 shadow-md shadow-primary-500/20" onClick={() => handleVerify('approved')}>
                        <CheckCircle size={18} /> Approve & Save
                    </button>
                    <button className="flex-1 justify-center py-2.5 rounded-lg border border-danger-200 text-danger-600 hover:bg-danger-50 transition-colors flex items-center gap-2 font-medium" onClick={() => handleVerify('rejected')}>
                        <XCircle size={18} /> Reject
                    </button>
                  </div>
                </div>
              )}

              {step === 'verified' && (
                <div className="mt-6 pt-5 border-t border-surface-200 text-center bg-primary-50 -mx-5 -mb-5 p-6 rounded-b-xl">
                  <CheckCircle size={32} className="text-primary-500 mx-auto mb-2" />
                  <p className="text-primary-700 font-bold text-lg">Verification Complete</p>
                  <p className="text-primary-600/70 text-sm mb-4">This action plan is now active on the dashboard.</p>
                  <button className="btn-primary mx-auto" onClick={() => navigate('/dashboard')}>View Dashboard</button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ConfidenceBadge({ score }: { score: number }) {
    if (!score && score !== 0) return null;
    let colorClass = score > 0.8 ? 'bg-primary-100 text-primary-700 border-primary-200' 
                   : score > 0.5 ? 'bg-amber-100 text-amber-700 border-amber-200'
                   : 'bg-danger-100 text-danger-700 border-danger-200';
    return (
        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono font-medium ${colorClass}`}>
            {(score * 100).toFixed(0)}%
        </span>
    );
}

function ExtractedFieldRow({ icon: Icon, label, field }: { icon: any; label: string; field: ExtractedField<any> | undefined }) {
  if (!field || !field.value) return null;
  const val = typeof field.value === 'string' ? field.value : JSON.stringify(field.value);
  if (!val) return null;

  return (
    <div className="group border-b border-surface-100 last:border-0 pb-3 last:pb-0">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-surface-500 uppercase tracking-wider flex items-center gap-1.5"><Icon size={12} /> {label}</span>
        <ConfidenceBadge score={field.confidence} />
      </div>
      <p className="text-sm text-surface-800 font-medium">{val}</p>
      {field.source_text && (
          <p className="text-[11px] text-surface-400 mt-1.5 italic bg-surface-50 px-2 py-1 rounded hidden group-hover:block transition-all">
            Quote: "{field.source_text}"
          </p>
      )}
    </div>
  );
}
