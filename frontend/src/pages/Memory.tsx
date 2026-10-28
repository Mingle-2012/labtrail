import { useState, useEffect } from 'react'
import { useApp } from '../App'
import { Brain, Plus, Trash2, Search, RefreshCw } from 'lucide-react'

const API_BASE = '/api'

const MEMORY_TYPES = [
  { value: 'conclusion', label: '研究结论', color: 'badge-green' },
  { value: 'decision', label: '技术决策', color: 'badge-blue' },
  { value: 'plan', label: '研究计划', color: 'badge-purple' },
  { value: 'failure', label: '失败方案', color: 'badge-red' },
  { value: 'general', label: '一般记忆', color: 'badge-amber' },
]

export default function Memory() {
  const { currentProject } = useApp()
  const [memories, setMemories] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [content, setContent] = useState('')
  const [memoryType, setMemoryType] = useState('conclusion')
  const [tags, setTags] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [context, setContext] = useState('')

  const loadMemories = async () => {
    if (!currentProject) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/memory/${currentProject.id}`)
      const data = await res.json()
      setMemories(data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { loadMemories() }, [currentProject])

  const handleSave = async () => {
    if (!content.trim() || !currentProject) return
    try {
      await fetch(`${API_BASE}/memory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProject.id,
          content,
          memory_type: memoryType,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        }),
      })
      setContent('')
      setTags('')
      setShowForm(false)
      loadMemories()
    } catch (e) { console.error(e) }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim() || !currentProject) return
    try {
      const res = await fetch(`${API_BASE}/memory/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentProject.id, query: searchQuery, n_results: 5 }),
      })
      const data = await res.json()
      setSearchResults(data.results || [])
    } catch (e) { console.error(e) }
  }

  const loadContext = async () => {
    if (!currentProject) return
    try {
      const res = await fetch(`${API_BASE}/memory/${currentProject.id}/context`)
      const data = await res.json()
      setContext(data.context)
    } catch (e) { console.error(e) }
  }

  const handleDelete = async (memoryId: string) => {
    if (!currentProject) return
    try {
      await fetch(`${API_BASE}/memory/${currentProject.id}/${memoryId}`, { method: 'DELETE' })
      loadMemories()
    } catch (e) { console.error(e) }
  }

  const getTypeInfo = (type: string) => MEMORY_TYPES.find(t => t.value === type) || MEMORY_TYPES[4]

  if (!currentProject) return <div className="empty-state"><p>请先选择一个项目</p></div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Brain size={24} /> 长期研究记忆
        </h1>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={loadContext}>
            <RefreshCw size={16} /> 恢复上下文
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} /> 保存记忆
          </button>
        </div>
      </div>

      <div className="mb-4 p-3 bg-purple-50 border border-purple-100 rounded-lg text-sm text-purple-700">
        研究记忆通过 PowerContext 持久化存储，支持跨会话恢复。记忆与项目隔离，每个项目独立管理。
      </div>

      {showForm && (
        <div className="card mb-6">
          <h3 className="card-title mb-3">保存新的研究记忆</h3>
          <textarea
            className="textarea mb-3"
            placeholder="例如：当前我们认为 OOD 查询分布与 base 分布之间的差异可能影响图索引搜索性能..."
            value={content}
            onChange={e => setContent(e.target.value)}
            rows={3}
          />
          <div className="flex gap-3 mb-3">
            <select className="input w-40" value={memoryType} onChange={e => setMemoryType(e.target.value)}>
              {MEMORY_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <input
              className="input flex-1"
              placeholder="标签（逗号分隔）"
              value={tags}
              onChange={e => setTags(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <button className="btn btn-primary" onClick={handleSave}>保存到 PowerContext</button>
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>取消</button>
          </div>
        </div>
      )}

      {context && (
        <div className="card mb-6 border-blue-200 bg-blue-50">
          <h3 className="card-title mb-2 text-blue-800">已恢复的研究上下文</h3>
          <pre className="text-sm text-blue-700 whitespace-pre-wrap font-sans">{context}</pre>
        </div>
      )}

      <div className="card mb-6">
        <h3 className="card-title mb-3">搜索记忆</h3>
        <div className="flex gap-2">
          <input
            className="input flex-1"
            placeholder="搜索研究记忆..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-secondary" onClick={handleSearch}>
            <Search size={16} /> 搜索
          </button>
        </div>
        {searchResults.length > 0 && (
          <div className="mt-3 space-y-2">
            {searchResults.map((r: any, i: number) => (
              <div key={i} className="p-2 bg-gray-50 rounded text-sm">
                <p>{r.content}</p>
                <p className="text-xs text-gray-500 mt-1">检索得分: {Number(r.score).toFixed(3)}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">已保存的记忆 ({memories.length})</h3>
        </div>
        {loading ? <div className="loading"><div className="spinner" /></div> : memories.length === 0 ? (
          <div className="empty-state">
            <Brain size={48} className="text-gray-300 mb-3" />
            <p className="text-lg font-medium mb-1">暂无研究记忆</p>
            <p className="text-sm">保存研究结论、决策和计划，支持跨会话恢复</p>
          </div>
        ) : (
          <div className="space-y-3">
            {memories.map((m: any, i: number) => {
              const typeInfo = getTypeInfo(m.metadata?.memory_type || 'general')
              return (
                <div key={i} className="p-3 border border-[var(--color-border)] rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <span className={`badge ${typeInfo.color}`}>{typeInfo.label}</span>
                    <button className="text-gray-400 hover:text-red-500" onClick={() => handleDelete(m.id || i)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                  <p className="text-sm">{m.content}</p>
                  {m.metadata?.tags && (
                    <div className="flex gap-1 mt-2">
                      {m.metadata.tags.split(',').filter(Boolean).map((t: string, j: number) => (
                        <span key={j} className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
