import { useState, useEffect, useRef } from 'react'
import { useApp } from '../App'
import { Upload, FlaskConical, BarChart3 } from 'lucide-react'
import {
  BarChart, Bar, ResponsiveContainer, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'

const API_BASE = '/api'

export default function Experiments() {
  const { currentProject } = useApp()
  const [data, setData] = useState<any>(null)
  const [recallQps, setRecallQps] = useState<any>({})
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [filterMethod, setFilterMethod] = useState('')
  const [filterDataset, setFilterDataset] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadData = async () => {
    if (!currentProject) return
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filterMethod) params.set('method', filterMethod)
      if (filterDataset) params.set('dataset', filterDataset)
      const res = await fetch(`${API_BASE}/experiments/${currentProject.id}?${params}`)
      const result = await res.json()
      setData(result)

      const res2 = await fetch(`${API_BASE}/experiments/${currentProject.id}/recall-qps`)
      const rqData = await res2.json()
      setRecallQps(rqData)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => { loadData() }, [currentProject, filterMethod, filterDataset])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !currentProject) return
    setUploading(true)
    const formData = new FormData()
    formData.append('project_id', currentProject.id)
    formData.append('file', file)
    try {
      const res = await fetch(`${API_BASE}/experiments/upload`, { method: 'POST', body: formData })
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail) }
      loadData()
    } catch (e: any) { alert(e.message) }
    setUploading(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  if (!currentProject) return <div className="empty-state"><p>请先选择一个项目</p></div>

  const methods = data?.methods || []
  const datasets = data?.datasets || []
  const records = data?.records || []

  const buildTimeData = methods.flatMap((method: string) => {
    const methodRecords = records.filter((r: any) => r.method === method && r.metric_name === 'index_build_time')
    return methodRecords.map((r: any) => ({ method, dataset: r.dataset, time: r.metric_value }))
  })

  const memoryData = methods.flatMap((method: string) => {
    const methodRecords = records.filter((r: any) => r.method === method && (r.metric_name === 'peak_memory' || r.metric_name === 'memory'))
    return methodRecords.map((r: any) => ({ method, dataset: r.dataset, memory: r.metric_value }))
  })

  const recallQpsPoints = Object.entries(recallQps).flatMap(([method, points]: [string, any]) =>
    (points as any[]).map((p: any) => ({ method, recall: p.recall, qps: p.qps, dataset: p.dataset }))
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FlaskConical size={24} /> 实验数据分析
        </h1>
        <div className="flex gap-2">
          <input ref={fileInputRef} type="file" accept=".csv" onChange={handleUpload} className="hidden" id="exp-upload" />
          <label htmlFor="exp-upload" className="btn btn-primary cursor-pointer">
            <Upload size={16} />
            {uploading ? '导入中...' : '导入 CSV'}
          </label>
        </div>
      </div>

      <div className="flex gap-3 mb-4">
        <select className="input w-48" value={filterMethod} onChange={e => setFilterMethod(e.target.value)}>
          <option value="">全部方法</option>
          {methods.map((m: string) => <option key={m} value={m}>{m}</option>)}
        </select>
        <select className="input w-48" value={filterDataset} onChange={e => setFilterDataset(e.target.value)}>
          <option value="">全部数据集</option>
          {datasets.map((d: string) => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      {loading ? <div className="loading"><div className="spinner" /></div> : !data?.total_records ? (
        <div className="empty-state">
          <BarChart3 size={48} className="text-gray-300 mb-3" />
          <p className="text-lg font-medium mb-1">暂无实验数据</p>
          <p className="text-sm">上传 CSV 文件导入实验结果</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="card text-center">
              <p className="text-3xl font-bold text-[var(--color-primary)]">{data.total_records}</p>
              <p className="text-sm text-[var(--color-text-secondary)]">实验记录总数</p>
            </div>
            <div className="card text-center">
              <p className="text-3xl font-bold text-green-600">{methods.length}</p>
              <p className="text-sm text-[var(--color-text-secondary)]">算法方法</p>
            </div>
            <div className="card text-center">
              <p className="text-3xl font-bold text-purple-600">{datasets.length}</p>
              <p className="text-sm text-[var(--color-text-secondary)]">测试数据集</p>
            </div>
          </div>

          <div className="card mb-6">
            <h3 className="card-title mb-4">实验结果表</h3>
            <div className="overflow-x-auto">
              <table>
                <thead>
                  <tr>
                    <th>方法</th>
                    <th>数据集</th>
                    <th>指标</th>
                    <th>值</th>
                    <th>参数</th>
                  </tr>
                </thead>
                <tbody>
                  {records.slice(0, 50).map((r: any, i: number) => (
                    <tr key={i}>
                      <td><span className="badge badge-blue">{r.method}</span></td>
                      <td>{r.dataset}</td>
                      <td className="font-mono text-xs">{r.metric_name}</td>
                      <td className="font-mono font-medium">{r.metric_value?.toFixed(4)}</td>
                      <td className="text-xs text-[var(--color-text-secondary)]">
                        {r.parameters ? JSON.stringify(r.parameters).substring(0, 60) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="card">
              <h3 className="card-title mb-4">Recall-QPS 曲线</h3>
              {recallQpsPoints.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="recall" name="Recall" label={{ value: 'Recall@10', position: 'bottom' }} />
                    <YAxis dataKey="qps" name="QPS" label={{ value: 'QPS', angle: -90, position: 'left' }} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    {methods.map((m: string, i: number) => {
                      const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                      const pts = recallQpsPoints.filter(p => p.method === m)
                      return <Scatter key={m} name={m} data={pts} fill={colors[i % colors.length]} />
                    })}
                  </ScatterChart>
                </ResponsiveContainer>
              ) : <p className="text-sm text-gray-400 text-center py-8">无 Recall-QPS 数据</p>}
            </div>

            <div className="card">
              <h3 className="card-title mb-4">构建时间对比</h3>
              {buildTimeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={buildTimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="dataset" tick={{ fontSize: 10 }} />
                    <YAxis label={{ value: '秒', angle: -90, position: 'left' }} />
                    <Tooltip />
                    <Legend />
                    {methods.map((m: string, i: number) => {
                      const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444']
                      return <Bar key={m} dataKey="time" name={m} fill={colors[i % colors.length]} />
                    })}
                  </BarChart>
                </ResponsiveContainer>
              ) : <p className="text-sm text-gray-400 text-center py-8">无构建时间数据</p>}
            </div>
          </div>

          <div className="card">
            <h3 className="card-title mb-4">内存开销对比</h3>
            {memoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={memoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dataset" tick={{ fontSize: 10 }} />
                  <YAxis label={{ value: 'MB', angle: -90, position: 'left' }} />
                  <Tooltip />
                  <Legend />
                  {methods.map((m: string, i: number) => {
                    const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444']
                    return <Bar key={m} dataKey="memory" name={m} fill={colors[i % colors.length]} />
                  })}
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="text-sm text-gray-400 text-center py-8">无内存数据</p>}
          </div>
        </>
      )}
    </div>
  )
}
