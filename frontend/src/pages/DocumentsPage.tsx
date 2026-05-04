import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Trash2, Eye, Clock, Loader2 } from 'lucide-react';
import { listDocuments, deleteDocument } from '../services/api';
import type { Document } from '../types';

const statusColors: Record<string, string> = {
  uploaded: 'badge-info',
  processing: 'badge-medium',
  extracted: 'badge-medium',
  action_generated: 'badge-medium',
  verified: 'badge-low',
  rejected: 'badge-high',
};

const statusLabels: Record<string, string> = {
  uploaded: 'Uploaded',
  processing: 'Processing',
  extracted: 'Extracted',
  action_generated: 'Pending Review',
  verified: 'Verified',
  rejected: 'Rejected',
};

export default function DocumentsPage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await listDocuments();
      setDocuments(res.documents);
    } catch (err) {
      console.error('Failed to load documents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this document?')) return;
    try {
      await deleteDocument(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error('Delete failed', err);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-surface-900">Documents</h1>
          <p className="text-surface-500 mt-1">All uploaded court judgments</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/upload')}>
          <FileText size={16} /> Upload New
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="text-primary-500 animate-spin" />
        </div>
      ) : documents.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <FileText size={48} className="text-surface-300 mx-auto mb-4" />
          <p className="text-surface-500 text-lg">No documents uploaded yet</p>
          <button className="btn-primary mt-6" onClick={() => navigate('/upload')}>
            Upload Your First PDF
          </button>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Pages</th>
                <th>Size</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr
                  key={doc.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/review/${doc.id}`)}
                >
                  <td>
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center border border-primary-100">
                        <FileText size={16} className="text-primary-600" />
                      </div>
                      <span className="font-medium text-surface-700 truncate max-w-[250px]">
                        {doc.original_filename}
                      </span>
                    </div>
                  </td>
                  <td className="text-surface-500">{doc.page_count}</td>
                  <td className="text-surface-500">{formatSize(doc.file_size)}</td>
                  <td>
                    <span className={`badge ${statusColors[doc.status] || 'badge-info'}`}>
                      {statusLabels[doc.status] || doc.status}
                    </span>
                  </td>
                  <td className="text-surface-500 text-sm">
                    <div className="flex items-center gap-1.5">
                      <Clock size={13} />
                      {formatDate(doc.upload_date)}
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <button
                        className="p-2 rounded-lg hover:bg-primary-50 text-surface-400 hover:text-primary-600 transition"
                        onClick={(e) => { e.stopPropagation(); navigate(`/review/${doc.id}`); }}
                        title="Review"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        className="p-2 rounded-lg hover:bg-red-50 text-surface-400 hover:text-danger-500 transition"
                        onClick={(e) => handleDelete(doc.id, e)}
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
