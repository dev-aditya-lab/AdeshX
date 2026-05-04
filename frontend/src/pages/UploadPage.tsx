import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadDocument } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadStatus('error');
      setErrorMsg('Only PDF files are accepted');
      return;
    }

    setUploading(true);
    setUploadStatus('idle');
    try {
      const doc = await uploadDocument(file);
      setUploadStatus('success');
      setTimeout(() => navigate(`/review/${doc.id}`), 1000);
    } catch (err: any) {
      setUploadStatus('error');
      setErrorMsg(err?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const onDragLeave = useCallback(() => setIsDragActive(false), []);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-surface-900 mb-2">Upload Court Judgment</h1>
        <p className="text-surface-500 text-base">
          Upload a PDF of a court judgment to extract information and generate action plans.
        </p>
      </div>

      {/* Upload Zone */}
      <div
        className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={onFileSelect}
          className="hidden"
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-4">
            <Loader2 size={48} className="text-primary-500 animate-spin" />
            <p className="text-lg text-surface-600">Uploading document...</p>
          </div>
        ) : uploadStatus === 'success' ? (
          <div className="flex flex-col items-center gap-4">
            <CheckCircle size={48} className="text-primary-500" />
            <p className="text-lg text-primary-600 font-semibold">Upload successful!</p>
            <p className="text-sm text-surface-500">Redirecting to review...</p>
          </div>
        ) : uploadStatus === 'error' ? (
          <div className="flex flex-col items-center gap-4">
            <AlertCircle size={48} className="text-danger-500" />
            <p className="text-lg text-danger-600 font-semibold">Upload failed</p>
            <p className="text-sm text-surface-500">{errorMsg}</p>
            <button className="btn-secondary mt-2" onClick={(e) => { e.stopPropagation(); setUploadStatus('idle'); }}>
              Try Again
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <div className="w-20 h-20 rounded-2xl bg-primary-50 flex items-center justify-center border border-primary-100">
              <Upload size={32} className="text-primary-500" />
            </div>
            <div>
              <p className="text-lg text-surface-700 font-medium">
                Drag & drop your PDF here
              </p>
              <p className="text-sm text-surface-400 mt-1">
                or click to browse · PDF files only · Max 50MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Features */}
      <div className="grid grid-cols-3 gap-4 mt-10">
        {[
          { icon: FileText, title: 'Text Extraction', desc: 'Digital + OCR support' },
          { icon: Upload, title: 'AI Analysis', desc: 'NLP-powered extraction' },
          { icon: CheckCircle, title: 'Action Plans', desc: 'Auto-generated plans' },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="glass-card p-5 text-center">
            <Icon size={24} className="text-primary-500 mx-auto mb-3" />
            <p className="text-sm font-semibold text-surface-700">{title}</p>
            <p className="text-xs text-surface-400 mt-1">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
