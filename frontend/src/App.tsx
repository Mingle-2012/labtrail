import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect, createContext, useContext } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Library from './pages/Library'
import Search from './pages/Search'
import Experiments from './pages/Experiments'
import Memory from './pages/Memory'
import Reports from './pages/Reports'
import Projects from './pages/Projects'

interface Project {
  id: string
  name: string
  description: string
  research_direction: string
  goal: string
  created_at: string
  updated_at: string
}

interface AppContextType {
  currentProject: Project | null
  setCurrentProject: (p: Project | null) => void
  projects: Project[]
  refreshProjects: () => void
}

export const AppContext = createContext<AppContextType>({
  currentProject: null,
  setCurrentProject: () => {},
  projects: [],
  refreshProjects: () => {},
})

export const useApp = () => useContext(AppContext)

const API_BASE = '/api'

function App() {
  const [projects, setProjects] = useState<Project[]>([])
  const [currentProject, setCurrentProject] = useState<Project | null>(null)

  const refreshProjects = async () => {
    try {
      const res = await fetch(`${API_BASE}/projects`)
      const data = await res.json()
      setProjects(data)
      if (!currentProject && data.length > 0) {
        setCurrentProject(data[0])
      }
    } catch (e) {
      console.error('Failed to load projects:', e)
    }
  }

  useEffect(() => {
    refreshProjects()
  }, [])

  return (
    <AppContext.Provider value={{ currentProject, setCurrentProject, projects, refreshProjects }}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="library" element={<Library />} />
            <Route path="search" element={<Search />} />
            <Route path="experiments" element={<Experiments />} />
            <Route path="memory" element={<Memory />} />
            <Route path="reports" element={<Reports />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppContext.Provider>
  )
}

export default App
