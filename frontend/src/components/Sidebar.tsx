import { NavLink } from 'react-router-dom';
import { Upload, FileText, LayoutDashboard, Shield } from 'lucide-react';

const navItems = [
  { to: '/upload', label: 'Upload PDF', icon: Upload },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-[260px] flex flex-col border-r border-surface-200 bg-white/80 backdrop-blur-xl z-50">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-surface-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-md shadow-primary-500/20">
            <Shield size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-surface-900 tracking-tight">AdeshX</h1>
            <p className="text-[11px] text-surface-500 leading-tight">Judgments → Action</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary-50 text-primary-700 border border-primary-200 shadow-sm'
                  : 'text-surface-500 hover:text-surface-800 hover:bg-surface-100'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-surface-200">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
          <span className="text-xs text-surface-500">AI Engine Active</span>
        </div>
      </div>
    </aside>
  );
}
