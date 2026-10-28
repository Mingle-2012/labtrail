import { useState } from 'react'
import { useApp } from '../App'
import { FileText, Download, Sparkles } from 'lucide-react'

const API_BASE = '/api'

export default function Reports() {
  const { currentProject } = useApp()
  const [report, setReport] = useState('')
  const [loading, setLoading] = useState(false)
  const [llmKey, setLlmKey] = useState('')
  const [useLlm, setUseLlm] = useState(false)

  const generateReport = async () => {
    if (!currentProject) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/reports/weekly`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProject.id,
          llm_api_key: useLlm && llmKey ? llmKey : null,
        }),
      })
      if (!res.ok) throw new Error('Failed to generate report')
      const data = await res.json()
      setReport(data.report)
    } catch (e: any) {
      alert(e.message)
    }
    setLoading(false)
  }

  const handleExport = () => {
    if (!report) return
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-report-${currentProject?.name?.replace(/\s+/g, '-')}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!currentProject) return <div className="empty-state"><p>请先选择一个项目</p></div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText size={24} /> 科研周报生成器
        </h1>
        <div className="flex gap-2">
          <button className="btn btn-primary" onClick={generateReport} disabled={loading}>
            <Sparkles size={16} />
            {loading ? '生成中...' : '生成周报'}
          </button>
          {report && (
            <button className="btn btn-secondary" onClick={handleExport}>
              <Download size={16} /> 导出 Markdown
            </button>
          )}
        </div>
      </div>

      <div className="mb-4 p-3 bg-amber-50 border border-amber-100 rounded-lg text-sm text-amber-700">
        周报基于 seekdb 中的文档记录、实验数据和 PowerContext 中的研究记忆自动生成。
        所有实验数字均可追溯到原始 CSV 记录。
      </div>

      <div className="card mb-6">
        <h3 className="card-title mb-3">生成选项</h3>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={useLlm}
              onChange={e => setUseLlm(e.target.checked)}
              className="rounded"
            />
            使用 LLM 增强（可选，需提供 API Key）
          </label>
          {useLlm && (
            <input
              className="input flex-1"
              placeholder="OpenAI-compatible API Key"
              type="password"
              value={llmKey}
              onChange={e => setLlmKey(e.target.value)}
            />
          )}
        </div>
        <p className="text-xs text-[var(--color-text-secondary)] mt-2">
          未配置 LLM API Key 时，将使用模板生成结构化报告。API Key 不会被保存到服务器。
        </p>
      </div>

      {report ? (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">科研周报</h3>
            <span className="text-xs text-[var(--color-text-secondary)]">
              生成时间: {new Date().toLocaleString()}
            </span>
          </div>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed bg-gray-50 p-4 rounded-lg">
              {report}
            </pre>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <FileText size={48} className="text-gray-300 mb-3" />
          <p className="text-lg font-medium mb-1">点击"生成周报"开始</p>
          <p className="text-sm">系统将基于项目数据自动生成科研周报</p>
        </div>
      )}
    </div>
  )
}
