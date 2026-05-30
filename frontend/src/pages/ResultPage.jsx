import { useState } from 'react'
import {
  ArrowLeft, FileText, CheckCircle2, AlertTriangle, AlertOctagon,
  FlaskConical, MessageSquare, ChevronDown, ChevronUp,
  Scan, ClipboardList, Download, Loader2
} from 'lucide-react'
import FindingCard from '../components/FindingCard'
import { useLang } from '../context/LangContext'
import { api } from '../api'
import './ResultPage.css'

export default function ResultPage({ result, onBack }) {
  const { t } = useLang()
  const [showNormal,    setShowNormal]    = useState(false)
  const [exporting,     setExporting]     = useState(false)
  const [exportError,   setExportError]   = useState('')

  if (!result) return null
  const { report_id, filename, patient_name, summary, findings, questions, stats, is_scanned } = result
  const flagged = findings.filter(f => f.flag)
  const normal  = findings.filter(f => !f.flag)

  const handleExport = async () => {
    setExporting(true); setExportError('')
    try {
      const url = await api.exportPDF(report_id)
      const a   = document.createElement('a')
      a.href    = url
      a.download = `medeasy_${(patient_name || 'report').replace(/\s+/g,'_')}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setExportError(err.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="result-page">
      {/* Top bar */}
      <div className="result-topbar animate-slide-left">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={16} /><span>{t.backToUpload}</span>
        </button>
        <button className="export-btn" onClick={handleExport} disabled={exporting}>
          {exporting
            ? <><Loader2 size={15} className="spin-icon" /><span>Exporting...</span></>
            : <><Download size={15} /><span>{t.exportPDF}</span></>
          }
        </button>
      </div>
      {exportError && <div className="export-error animate-fade-in">{exportError}</div>}

      {/* Header */}
      <div className="result-header animate-fade-in-up">
        <div className="result-header-icon"><FileText size={22} /></div>
        <div className="result-header-info">
          <h2 className="result-title">
            {patient_name ? `${patient_name}'s Report` : 'Report Analysis'}
          </h2>
          <div className="result-meta">
            <span className="meta-item"><FileText size={12} />{filename}</span>
            {is_scanned && (
              <span className="meta-badge scanned"><Scan size={11} />Scanned PDF</span>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid animate-fade-in-up">
        {[
          { cls:'',       Icon: FlaskConical,  num: stats.total,    label: t.totalTests },
          { cls:'green',  Icon: CheckCircle2,  num: stats.normal,   label: t.normal },
          { cls:'orange', Icon: AlertTriangle, num: stats.flagged,  label: t.needAttention },
          { cls:'red',    Icon: AlertOctagon,  num: stats.critical, label: t.critical },
        ].map(({ cls, Icon, num, label }, i) => (
          <div key={i} className={`stat-card ${cls}`} style={{ animationDelay:`${i*0.07}s` }}>
            <div className={`stat-icon ${cls || 'neutral'}`}><Icon size={18} /></div>
            <div className="stat-num">{num}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="summary-card animate-fade-in-up">
        <div className="summary-header">
          <div className="summary-icon"><ClipboardList size={16} /></div>
          <span className="summary-title">{t.overallSummary}</span>
        </div>
        <p className="summary-text">{summary}</p>
      </div>

      {/* Flagged */}
      {flagged.length > 0 && (
        <section className="findings-section animate-fade-in-up">
          <div className="section-header flagged">
            <AlertTriangle size={16} />
            <span>{t.valuesAttention}</span>
            <span className="section-count">{flagged.length}</span>
          </div>
          {flagged.map((f, i) => <FindingCard key={i} finding={f} index={i} />)}
        </section>
      )}

      {/* Normal */}
      {normal.length > 0 && (
        <section className="findings-section animate-fade-in-up">
          <button className="toggle-btn" onClick={() => setShowNormal(v => !v)}>
            <div className="toggle-btn-left">
              <CheckCircle2 size={16} />
              <span>{t.normalValues}</span>
              <span className="section-count normal">{normal.length}</span>
            </div>
            {showNormal ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {showNormal && (
            <div className="normal-findings animate-fade-in">
              {normal.map((f, i) => <FindingCard key={i} finding={f} index={i} />)}
            </div>
          )}
        </section>
      )}

      {/* Questions */}
      {questions?.length > 0 && (
        <div className="questions-card animate-fade-in-up">
          <div className="questions-header">
            <div className="questions-icon"><MessageSquare size={16} /></div>
            <div>
              <div className="questions-title">{t.askDoctor}</div>
              <div className="questions-sub">{t.askDoctorSub}</div>
            </div>
          </div>
          <ol className="questions-list">
            {questions.map((q, i) => (
              <li key={i} className="question-item" style={{ animationDelay:`${i*0.07}s` }}>
                <span className="question-num">{i+1}</span>
                <span>{q}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="result-footer">
        MedEasy uses Groq AI (Llama 3.3). Always verify results with a qualified medical professional.
      </div>
    </div>
  )
}
