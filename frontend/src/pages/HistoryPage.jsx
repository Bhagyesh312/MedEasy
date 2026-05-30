import { useState, useEffect } from 'react'
import { ArrowLeft, FileText, User, Clock, Trash2, AlertTriangle, FlaskConical, Inbox, RefreshCw, GitCompare } from 'lucide-react'
import { useLang } from '../context/LangContext'
import { api } from '../api'
import './HistoryPage.css'

export default function HistoryPage({ onBack }) {
  const { t } = useLang()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  const fetchReports = async () => {
    setLoading(true); setError('')
    try {
      const data = await api.getReports()
      setReports(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchReports() }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this report permanently?')) return
    try {
      await api.deleteReport(id)
      setReports(prev => prev.filter(r => r.id !== id))
    } catch (err) {
      alert(err.message)
    }
  }

  const formatDate = (iso) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleString('en-IN', {
      day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'
    })
  }

  return (
    <div className="history-page">
      <div className="history-topbar animate-slide-left">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={16} /><span>Back</span>
        </button>
        <button className="refresh-btn" onClick={fetchReports} disabled={loading}>
          <RefreshCw size={15} className={loading ? 'spin-icon' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="history-header animate-fade-in-up">
        <div className="history-header-icon"><Clock size={22} /></div>
        <div>
          <h2 className="history-title">{t.history}</h2>
          <p className="history-sub">All your previously analysed reports</p>
        </div>
      </div>

      {loading && (
        <div className="skeleton-list">
          {[1,2,3].map(i => (
            <div key={i} className="skeleton-card">
              <div className="skeleton-line wide" />
              <div className="skeleton-line medium" />
              <div className="skeleton-line short" />
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="history-error animate-fade-in">
          <AlertTriangle size={18} />
          <div>
            <div className="error-title">{error}</div>
            <div className="error-hint">Make sure the Flask backend is running on port 5000.</div>
          </div>
        </div>
      )}

      {!loading && !error && reports.length === 0 && (
        <div className="history-empty animate-scale-in">
          <div className="empty-icon-wrap"><Inbox size={32} /></div>
          <div className="empty-title">{t.noHistory}</div>
          <div className="empty-sub">{t.noHistorySub}</div>
          <button className="empty-cta" onClick={onBack}>Upload your first report</button>
        </div>
      )}

      {!loading && !error && reports.length > 0 && (
        <div className="reports-list">
          {reports.map((r, i) => (
            <div key={r.id} className="report-row animate-fade-in-up"
              style={{ animationDelay:`${i*0.06}s` }}>
              <div className="report-row-icon"><FileText size={18} /></div>
              <div className="report-row-info">
                <div className="report-filename">{r.filename}</div>
                <div className="report-meta-row">
                  {r.patient_name && (
                    <span className="report-meta-item"><User size={11} />{r.patient_name}</span>
                  )}
                  <span className="report-meta-item"><Clock size={11} />{formatDate(r.uploaded_at)}</span>
                </div>
              </div>
              <div className="report-row-badges">
                <span className="badge total"><FlaskConical size={11} />{r.total_tests} tests</span>
                {r.flagged_count > 0 && (
                  <span className="badge flagged"><AlertTriangle size={11} />{r.flagged_count} flagged</span>
                )}
                <span className={`badge status ${r.status}`}>{r.status}</span>
              </div>
              <button className="delete-btn" onClick={() => handleDelete(r.id)} title="Delete">
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
