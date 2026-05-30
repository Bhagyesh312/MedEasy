import { useState } from 'react'
import { useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import AuthPage from './pages/AuthPage'
import UploadPage from './pages/UploadPage'
import ResultPage from './pages/ResultPage'
import HistoryPage from './pages/HistoryPage'
import ComparePage from './pages/ComparePage'
import NotFoundPage from './pages/NotFoundPage'
import Spinner from './components/Spinner'
import './App.css'

const VALID_PAGES = ['upload', 'result', 'history', 'compare']

export default function App() {
  const { user, loading } = useAuth()
  const [page,   setPage]   = useState('upload')
  const [result, setResult] = useState(null)

  if (loading) return (
    <div className="app-loading">
      <Spinner size={36} />
    </div>
  )

  if (!user) return <AuthPage />

  const goTo = (p, data = null) => {
    if (data) setResult(data)
    setPage(VALID_PAGES.includes(p) ? p : '404')
  }

  return (
    <div className="app">
      <Navbar page={page} goTo={goTo} />
      <main className="main-content">
        {page === 'upload'  && <UploadPage  onResult={d => goTo('result', d)} />}
        {page === 'result'  && <ResultPage  result={result} onBack={() => goTo('upload')} />}
        {page === 'history' && <HistoryPage onBack={() => goTo('upload')} />}
        {page === 'compare' && <ComparePage onBack={() => goTo('history')} />}
        {page === '404'     && <NotFoundPage onBack={() => goTo('upload')} />}
      </main>
    </div>
  )
}
