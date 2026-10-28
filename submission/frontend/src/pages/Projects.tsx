import { useState } from 'react'
import { useApp } from '../App'
import { Plus, FolderOpen, Trash2, Database } from 'lucide-react'

const API_BASE = '/api'

export default function Projects() {
  const { projects, refreshProjects, currentProject, setCurrentProject } = useApp()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [direction, setDirection] = useState('')
  const [goal, setGoal] = useState('')
  const [loadingDemo, setLoadingDemo] = useState(false)

  const handleCreate = async () => {
    if (!name.trim()) return
    try {
      const res = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, research_direction: direction, goal }),
      })
      const project = await res.json()
      refreshProjects()
      setCurrentProject(project)
      setShowForm(false)
      setName(''); setDescription(''); setDirection(''); setGoal('')
    } catch (e) { console.error(e) }
  }

  const handleDelete = async (id: string) => {
    try {
      await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' })
      if (currentProject?.id === id) setCurrentProject(null)
      refreshProjects()
    } catch (e) { console.error(e) }
  }

  const loadDemo = async () => {
    setLoadingDemo(true)
    try {
      const res = await fetch(`${API_BASE}/projects/demo_project`)
      if (res.ok) {
        const project = await res.json()
        setCurrentProject(project)
        refreshProjects()
        setLoadingDemo(false)
        return
      }
      const createRes = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Graph-based Approximate Nearest Neighbor Search',
          description: 'Research on graph-based indexing methods for ANN search, focusing on OOD query robustness.',
          research_direction: 'Graph-based ANN search, OOD robustness, query distribution-aware indexing',
          goal: 'Understand and mitigate OOD performance degradation in graph-based ANN indices',
        }),
      })
      const project = await createRes.json()
      setCurrentProject(project)
      refreshProjects()
    } catch (e) { console.error(e) }
    setLoadingDemo(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FolderOpen size={24} /> 研究项目管理
        </h1>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={loadDemo} disabled={loadingDemo}>
            <Database size={16} />
            {loadingDemo ? '加载中...' : '加载演示项目'}
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} /> 新建项目
          </button>
        </div>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="card-title mb-3">创建新研究项目</h3>
          <div className="space-y-3">
            <input className="input" placeholder="项目名称 *" value={name} onChange={e => setName(e.target.value)} />
            <textarea className="textarea" placeholder="项目描述" value={description} onChange={e => setDescription(e.target.value)} rows={2} />
            <input className="input" placeholder="研究方向" value={direction} onChange={e => setDirection(e.target.value)} />
            <input className="input" placeholder="当前研究目标" value={goal} onChange={e => setGoal(e.target.value)} />
            <div className="flex gap-2">
              <button className="btn btn-primary" onClick={handleCreate}>创建项目</button>
              <button className="btn btn-secondary" onClick={() => setShowForm(false)}>取消</button>
            </div>
          </div>
        </div>
      )}

      {projects.length === 0 ? (
        <div className="empty-state">
          <FolderOpen size={48} className="text-gray-300 mb-3" />
          <p className="text-lg font-medium mb-1">暂无研究项目</p>
          <p className="text-sm mb-4">创建新项目或加载演示项目开始使用</p>
          <div className="flex gap-2">
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              <Plus size={16} /> 新建项目
            </button>
            <button className="btn btn-secondary" onClick={loadDemo}>
              <Database size={16} /> 加载演示项目
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map(p => (
            <div
              key={p.id}
              className={`card cursor-pointer transition-shadow hover:shadow-sm ${
                currentProject?.id === p.id ? 'border-blue-300 bg-blue-50/30' : ''
              }`}
              onClick={() => setCurrentProject(p)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-lg">{p.name}</h3>
                    {currentProject?.id === p.id && (
                      <span className="badge badge-blue">当前项目</span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--color-text-secondary)] mb-2">{p.description}</p>
                  <div className="flex gap-4 text-xs text-[var(--color-text-secondary)]">
                    {p.research_direction && <span>方向: {p.research_direction}</span>}
                    <span>创建: {new Date(p.created_at).toLocaleDateString()}</span>
                    <span>更新: {new Date(p.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <button
                  className="text-gray-400 hover:text-red-500 p-1"
                  onClick={(e) => { e.stopPropagation(); handleDelete(p.id) }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
