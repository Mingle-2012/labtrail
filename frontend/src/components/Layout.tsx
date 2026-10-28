import { Outlet, NavLink } from 'react-router-dom'
import { useApp } from '../App'
import {
  LayoutDashboard, BookOpen, Search, FlaskConical, Brain, FileText, FolderOpen
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '工作台', end: true },
  { to: '/library', icon: BookOpen, label: '知识库' },
  { to: '/search', icon: Search, label: '检索' },
  { to: '/experiments', icon: FlaskConical, label: '实验分析' },
  { to: '/memory', icon: Brain, label: '研究记忆' },
  { to: '/reports', icon: FileText, label: '周报' },
  { to: '/projects', icon: FolderOpen, label: '项目' },
]

export default function Layout() {
  const { currentProject, projects, setCurrentProject } = useApp()

  return (
    <div className="flex h-screen bg-[var(--color-bg)]">
      <aside className="w-60 shrink-0 bg-white border-r border-[var(--color-border)] flex flex-col">
        <div className="p-4 border-b border-[var(--color-border)]">
          <h1 className="text-lg font-bold text-[var(--color-primary)]">LabTrail</h1>
          <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
            AI Research Workspace
          </p>
        </div>

        {projects.length > 0 && (
          <div className="px-3 py-3 border-b border-[var(--color-border)] flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[var(--color-text-secondary)]">
              当前项目
            </label>
            <select
              className="input text-sm min-w-0 truncate py-1.5"
              value={currentProject?.id || ''}
              onChange={(e) => {
                const p = projects.find(p => p.id === e.target.value)
                if (p) setCurrentProject(p)
              }}
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        )}

        <nav className="flex-1 p-2 space-y-0.5">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-[var(--color-primary)]'
                    : 'text-[var(--color-text-secondary)] hover:bg-gray-50 hover:text-[var(--color-text)]'
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-[var(--color-border)]">
          <p className="text-xs text-[var(--color-text-secondary)] text-center">
            Powered by seekdb & PowerContext
          </p>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
