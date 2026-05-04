import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import UploadPage from './pages/UploadPage';
import DocumentsPage from './pages/DocumentsPage';
import ReviewPage from './pages/ReviewPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen w-full">
        <Sidebar />
        <main className="flex-1 ml-[260px] p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/review/:id" element={<ReviewPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
