import { useState, useEffect, useRef } from 'react'
import { useApp } from '../App'
import { Upload, Trash2, FileText, FileSpreadsheet, File } from 'lucide-react'

const API_BASE = '/api'

export default function Library() {
  const { currentProject } = useApp()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadDocuments = async () => {
    if (!currentProject) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/documents/${currentProject.id}`)
      const data = await res.json()
      setDocuments(data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => { loadDocuments() }, [currentProject])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !currentProject) return

    setUploading(true)
    setError('')
    setSuccess('')

    const formData = new FormData()
    formData.append('project_id', currentProject.id)
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const data = await res.json()
      setSuccess(`已导入 "${file.name}"，共 ${data.chunks} 个文本块`)
      loadDocuments()
    } catch (e: any) {
      setError(e.message)
    }
    setUploading(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleDelete = async (docId: string) => {
    if (!currentProject) return
    try {
      await fetch(`${API_BASE}/documents/${currentProject.id}/${docId}`, { method: 'DELETE' })
      loadDocuments()
    } catch (e) {
      console.error(e)
    }
  }

  const getFileIcon = (type: string) => {
    if (type === '.csv') return <FileSpreadsheet size={16} className="text-green-600" />
    if (type === '.pdf') return <FileText size={16} className="text-red-600" />
    return <File size={16} className="text-blue-600" />
  }

  if (!currentProject) {
    return <div className="empty-state"><p>请先选择一个项目</p></div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">科研知识库</h1>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.md,.txt,.csv,.log"
            onChange={handleUpload}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="btn btn-primary cursor-pointer">
            <Upload size={16} />
            {uploading ? '导入中...' : '导入文件'}
          </label>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
          {success}
        </div>
      )}

      <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-700">
        支持格式：PDF、Markdown、TXT、CSV、LOG。文件将通过 seekdb 进行分块、向量化存储和索引。
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /></div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} className="text-gray-300 mb-3" />
          <p className="text-lg font-medium mb-1">暂无文档</p>
          <p className="text-sm">上传 PDF、Markdown 或 TXT 文件开始构建知识库</p>
        </div>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>文件名</th>
                <th>类型</th>
                <th>文本块</th>
                <th>导入时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc: any) => (
                <tr key={doc.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      {getFileIcon(doc.type)}
                      <span className="font-medium">{doc.name}</span>
                    </div>
                  </td>
                  <td><span className="badge badge-blue">{doc.type}</span></td>
                  <td>{doc.chunk_count}</td>
                  <td className="text-[var(--color-text-secondary)]">
                    {new Date(doc.created_at).toLocaleString()}
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash2 size={14} />
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
