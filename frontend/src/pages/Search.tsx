import { useState } from 'react'
import { useApp } from '../App'
import { Search as SearchIcon, FileText, Database, Zap } from 'lucide-react'

const API_BASE = '/api'

export default function Search() {
  const { currentProject } = useApp()
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState('hybrid')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!query.trim() || !currentProject) return
    setLoading(true)
    setSearched(true)
    try {
      const params = new URLSearchParams({ project_id: currentProject.id })
      const res = await fetch(`${API_BASE}/documents/search?${params}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, mode, n_results: 10 }),
      })
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      setResults(data.results || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  if (!currentProject) {
    return <div className="empty-state"><p>请先选择一个项目</p></div>
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <SearchIcon size={24} /> 智能证据检索
        </h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          基于 seekdb 的向量语义检索 + 全文检索混合搜索
        </p>
      </div>

      <div className="card mb-6">
        <div className="flex gap-3 mb-3">
          <div className="flex-1">
            <input
              className="input"
              placeholder="输入研究问题，例如：Why does OOD query distribution degrade graph index performance?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <select
            className="input w-36 shrink-0"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="hybrid">混合检索</option>
            <option value="vector">向量检索</option>
            <option value="fulltext">全文检索</option>
          </select>
          <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
            <Zap size={16} />
            {loading ? '检索中...' : '检索'}
          </button>
        </div>
        <div className="flex gap-4 text-xs text-[var(--color-text-secondary)]">
          <span className="flex items-center gap-1"><Database size={12} /> seekdb 向量索引</span>
          <span className="flex items-center gap-1"><FileText size={12} /> FULLTEXT 全文索引</span>
          <span className="flex items-center gap-1"><Zap size={12} /> {mode === 'hybrid' ? 'RRF 融合排序' : mode === 'vector' ? 'IVF 余弦检索' : '全文相关度排序'}</span>
        </div>
      </div>

      {searched && !loading && results.length === 0 && (
        <div className="empty-state">
          <SearchIcon size={48} className="text-gray-300 mb-3" />
          <p className="text-lg font-medium mb-1">未找到相关结果</p>
          <p className="text-sm">尝试使用不同的关键词或切换检索模式</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-[var(--color-text-secondary)]">
            找到 {results.length} 条结果（{mode === 'hybrid' ? '混合检索' : mode === 'vector' ? '向量检索' : '全文检索'}）
          </p>
          {results.map((r: any, i: number) => (
            <div key={i} className="card">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-[var(--color-primary)]" />
                  <span className="font-medium text-sm">
                    {r.metadata?.file_name || 'Unknown'}
                  </span>
                  {r.metadata?.page && (
                    <span className="badge badge-blue">第 {r.metadata.page} 页</span>
                  )}
                  {r.metadata?.file_type && (
                    <span className="badge badge-purple">{r.metadata.file_type}</span>
                  )}
                </div>
                <span className="text-xs text-[var(--color-text-secondary)]">
                  {mode === 'hybrid'
                    ? `RRF 融合分: ${Number(r.score).toFixed(4)}`
                    : mode === 'vector'
                      ? `余弦相似度: ${(r.score * 100).toFixed(1)}%`
                      : `全文得分: ${Number(r.score).toFixed(3)}`}
                </span>
              </div>
              <p className="text-sm leading-relaxed text-gray-700 bg-gray-50 p-3 rounded">
                {r.text?.substring(0, 500)}{r.text?.length > 500 ? '...' : ''}
              </p>
              {r.metadata?.source && (
                <p className="text-xs text-[var(--color-text-secondary)] mt-2">
                  来源: {r.metadata.source}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
