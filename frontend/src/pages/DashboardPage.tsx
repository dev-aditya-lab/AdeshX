import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, FileText, CheckCircle, Clock, AlertTriangle,
  Loader2, Filter, Building2, ArrowRight, Shield, TrendingUp
} from 'lucide-react';
import { getDashboardSummary, getDashboardCases, getDeadlines } from '../services/api';
import type { DashboardSummary, DashboardCase, UpcomingDeadline } from '../types';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [cases, setCases] = useState<DashboardCase[]>([]);
  const [deadlines, setDeadlines] = useState<UpcomingDeadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterPriority, setFilterPriority] = useState('');
  const [filterDept, setFilterDept] = useState('');

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { loadCases(); }, [filterPriority, filterDept]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [s, c, d] = await Promise.all([getDashboardSummary(), getDashboardCases(), getDeadlines()]);
      setSummary(s); setCases(c.cases); setDeadlines(d);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const loadCases = async () => {
    try {
      const filters: any = {};
      if (filterPriority) filters.priority = filterPriority;
      if (filterDept) filters.department = filterDept;
      const c = await getDashboardCases(filters);
      setCases(c.cases);
    } catch {}
  };

  if (loading) {
    return (<div className="flex items-center justify-center py-20"><Loader2 size={32} className="text-primary-500 animate-spin" /></div>);
  }

  const stats = [
    { label: 'Total Documents', value: summary?.total_documents ?? 0, icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Verified', value: summary?.verified ?? 0, icon: CheckCircle, color: 'text-primary-600', bg: 'bg-primary-50' },
    { label: 'Pending Review', value: summary?.pending_verification ?? 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'High Priority', value: summary?.high_priority ?? 0, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
  ];

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-surface-900 flex items-center gap-3">
          <LayoutDashboard size={28} className="text-primary-600" /> Dashboard
        </h1>
        <p className="text-surface-500 mt-1">Overview of verified cases and upcoming deadlines</p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="stat-card">
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center`}><Icon size={20} className={color} /></div>
              <TrendingUp size={14} className="text-surface-300" />
            </div>
            <p className="text-2xl font-bold text-surface-900">{value}</p>
            <p className="text-xs text-surface-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="glass-card overflow-hidden">
            <div className="px-5 py-4 border-b border-surface-200 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2">
                <Shield size={16} className="text-primary-600" /> Verified Cases
              </h3>
              <div className="flex items-center gap-2">
                <Filter size={14} className="text-surface-400" />
                <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)} className="input-field !py-1.5 !px-3 !text-xs !w-auto">
                  <option value="">All Priorities</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                <select value={filterDept} onChange={(e) => setFilterDept(e.target.value)} className="input-field !py-1.5 !px-3 !text-xs !w-auto">
                  <option value="">All Departments</option>
                  {summary?.departments.map(d => (<option key={d.department} value={d.department}>{d.department}</option>))}
                </select>
              </div>
            </div>

            {cases.length === 0 ? (
              <div className="p-12 text-center">
                <FileText size={40} className="text-surface-300 mx-auto mb-3" />
                <p className="text-surface-500">No verified cases yet</p>
                <p className="text-surface-400 text-sm mt-1">Upload and verify judgments to see them here</p>
              </div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Case</th><th>Action</th><th>Priority</th><th>Deadline</th><th>Department</th><th></th></tr></thead>
                <tbody>
                  {cases.map(c => (
                    <tr key={c.document_id} className="cursor-pointer" onClick={() => navigate(`/review/${c.document_id}`)}>
                      <td>
                        <div>
                          <p className="text-surface-700 font-medium text-sm truncate max-w-[200px]">{c.case_title}</p>
                          <p className="text-surface-400 text-xs">{c.case_number}</p>
                        </div>
                      </td>
                      <td><span className="badge badge-info text-[10px]">{c.action_required}</span></td>
                      <td><span className={`badge ${c.priority === 'high' ? 'badge-high' : c.priority === 'medium' ? 'badge-medium' : 'badge-low'} text-[10px]`}>{c.priority}</span></td>
                      <td className="text-surface-500 text-sm">{c.deadline || '—'}</td>
                      <td className="text-surface-500 text-xs truncate max-w-[140px]">{c.responsible_department}</td>
                      <td><ArrowRight size={14} className="text-surface-400" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card overflow-hidden">
            <div className="px-5 py-3 border-b border-surface-200">
              <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2"><Clock size={16} className="text-amber-500" /> Upcoming Deadlines</h3>
            </div>
            <div className="p-4 space-y-3 max-h-[300px] overflow-y-auto">
              {deadlines.length === 0 ? (
                <p className="text-surface-400 text-sm text-center py-4">No upcoming deadlines</p>
              ) : deadlines.map((d, i) => (
                <div key={i} className="p-3 rounded-lg bg-surface-100/60 border border-surface-200 cursor-pointer hover:border-primary-300 hover:bg-primary-50/30 transition" onClick={() => navigate(`/review/${d.document_id}`)}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-surface-700 truncate max-w-[160px]">{d.case_title}</span>
                    <span className={`badge text-[10px] ${d.priority === 'high' ? 'badge-high' : d.priority === 'medium' ? 'badge-medium' : 'badge-low'}`}>{d.priority}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-surface-500">{d.deadline}</span>
                    {d.days_remaining !== null && (
                      <span className={`text-xs font-bold ${d.days_remaining < 7 ? 'text-danger-500' : d.days_remaining < 30 ? 'text-warning-600' : 'text-primary-600'}`}>
                        {d.days_remaining < 0 ? 'OVERDUE' : `${d.days_remaining}d left`}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card overflow-hidden">
            <div className="px-5 py-3 border-b border-surface-200">
              <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2"><Building2 size={16} className="text-primary-600" /> Departments</h3>
            </div>
            <div className="p-4 space-y-2">
              {(!summary?.departments || summary.departments.length === 0) ? (
                <p className="text-surface-400 text-sm text-center py-4">No department data</p>
              ) : summary.departments.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 rounded-lg hover:bg-surface-100 transition">
                  <span className="text-sm text-surface-600 truncate max-w-[180px]">{d.department}</span>
                  <span className="text-xs font-bold text-primary-700 bg-primary-50 px-2.5 py-1 rounded-full border border-primary-100">{d.count}</span>
                </div>
              ))}
            </div>
          </div>

          {summary && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-surface-700 mb-4">Priority Breakdown</h3>
              <div className="space-y-3">
                {[
                  { label: 'High', value: summary.high_priority, color: '#ef4444', total: summary.verified || 1 },
                  { label: 'Medium', value: summary.medium_priority, color: '#f59e0b', total: summary.verified || 1 },
                  { label: 'Low', value: summary.low_priority, color: '#10b981', total: summary.verified || 1 },
                ].map(p => (
                  <div key={p.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-surface-500">{p.label}</span>
                      <span className="text-xs font-bold text-surface-700">{p.value}</span>
                    </div>
                    <div className="confidence-bar"><div className="confidence-bar-fill" style={{ width: `${(p.value / p.total) * 100}%`, background: p.color }} /></div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
