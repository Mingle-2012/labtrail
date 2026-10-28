import { useState, useEffect } from 'react'
import { useApp } from '../App'
import { BookOpen, FlaskConical, Brain, Search, FileText, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const API_BASE = '/api'

export default function Dashboard() {
  const { currentProject } = useApp()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!currentProject) return
    setLoading(true)
    fetch(`${API_BASE}/projects/${currentProject.id}/dashboard`)
      .then(r => r.json())
      .then(data => { setStats(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [currentProject])

  if (!currentProject) {
    return (
      <div className="empty-state">
        <h2 className="text-xl font-semibold mb-2">欢迎使用 LabTrail</h2>
        <p className="mb-4">请先创建一个研究项目或加载演示项目</p>
        <button className="btn btn-primary" onClick={() => navigate('/projects')}>
          管理项目
        </button>
      </div>
    )
  }

  if (loading) return <div className="loading"><div className="spinner" /></div>

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{currentProject.name}</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">{currentProject.description}</p>
        {currentProject.goal && (
          <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
            <span className="text-sm font-medium text-blue-800">研究目标：</span>
            <span className="text-sm text-blue-700">{currentProject.goal}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={<BookOpen size={20} />}
          label="文档数"
          value={stats?.total_documents || 0}
          color="blue"
          onClick={() => navigate('/library')}
        />
        <StatCard
          icon={<FlaskConical size={20} />}
          label="实验记录"
          value={stats?.total_experiments || 0}
          color="green"
          onClick={() => navigate('/experiments')}
        />
        <StatCard
          icon={<Brain size={20} />}
          label="研究记忆"
          value={stats?.methods?.length || 0}
          color="purple"
          onClick={() => navigate('/memory')}
        />
        <StatCard
          icon={<Search size={20} />}
          label="数据块"
          value={stats?.total_chunks || 0}
          color="amber"
          onClick={() => navigate('/search')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">最近活动</h3>
          </div>
          {stats?.recent_activities?.length > 0 ? (
            <div className="space-y-2">
              {stats.recent_activities.slice(0, 5).map((a: any, i: number) => (
                <div key={i} className="flex items-center gap-2 text-sm p-2 bg-gray-50 rounded">
                  <FileText size={14} className="text-[var(--color-text-secondary)]" />
                  <span>{a.name || a.type}</span>
                  <span className="ml-auto text-xs text-[var(--color-text-secondary)]">
                    {a.date ? new Date(a.date).toLocaleDateString() : ''}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-secondary)]">暂无活动记录</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">快速操作</h3>
          </div>
          <div className="space-y-2">
            <QuickAction icon={<Search size={16} />} label="搜索研究文献" onClick={() => navigate('/search')} />
            <QuickAction icon={<FlaskConical size={16} />} label="查看实验对比" onClick={() => navigate('/experiments')} />
            <QuickAction icon={<Brain size={16} />} label="保存研究记忆" onClick={() => navigate('/memory')} />
            <QuickAction icon={<FileText size={16} />} label="生成科研周报" onClick={() => navigate('/reports')} />
          </div>
        </div>
      </div>

      {stats?.methods?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">实验方法概览</h3>
          </div>
          <div className="flex gap-2 flex-wrap">
            {stats.methods.map((m: string) => (
              <span key={m} className="badge badge-blue">{m}</span>
            ))}
          </div>
          {stats.datasets?.length > 0 && (
            <div className="mt-3">
              <p className="text-sm text-[var(--color-text-secondary)] mb-1">数据集：</p>
              <div className="flex gap-2 flex-wrap">
                {stats.datasets.map((d: string) => (
                  <span key={d} className="badge badge-green">{d}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function StatCard({ icon, label, value, color, onClick }: any) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    amber: 'bg-amber-50 text-amber-600',
  }
  return (
    <div className="card cursor-pointer hover:shadow-sm transition-shadow" onClick={onClick}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}>{icon}</div>
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-xs text-[var(--color-text-secondary)]">{label}</p>
        </div>
      </div>
    </div>
  )
}

function QuickAction({ icon, label, onClick }: any) {
  return (
    <button
      className="w-full flex items-center gap-2 p-2 text-sm text-left rounded-lg hover:bg-gray-50 transition-colors"
      onClick={onClick}
    >
      <span className="text-[var(--color-primary)]">{icon}</span>
      <span>{label}</span>
      <ArrowRight size={14} className="ml-auto text-[var(--color-text-secondary)]" />
    </button>
  )
}
