import { useState, useRef } from 'react'
import { Upload, FileText, X, Loader2, ShieldCheck, Zap, Brain, ArrowRight, User } from 'lucide-react'
import { useLang } from '../context/LangContext'
import { api } from '../api'
import './UploadPage.css'

function validatePatientName(v) {
  if (!v.trim()) return ''                          // optional field — blank is fine
  if (v.trim().length < 2) return 'Name must be at least 2 characters.'
  if (v.trim().length > 50) return 'Name must be 50 characters or fewer.'
  if (/[0-9]/.test(v)) return 'Name cannot contain numbers.'
  if (/[^A-Za-z\u0900-\u097F\u0A80-\u0AFF\s\-'.]/.test(v))
    return 'Name can only contain letters, spaces, hyphens and dots.'
  return ''
}

export default function UploadPage({ onResult }) {
  const { lang, t } = useLang()
  const [file,        setFile]        = useState(null)
  const [patientName, setPatientName] = useState('')
  const [nameErr,     setNameErr]     = useState('')
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState('')
  const [dragOver,    setDragOver]    = useState(false)
  const inputRef = useRef()

  const handleFile = (f) => {
    if (!f) return
    if (!f.name.toLowerCase().endsWith('.pdf')) { setError('Only PDF files are supported.'); return }
    setError(''); setFile(f)
  }

  const handleDrop = (e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }

  const handleNameChange = (v) => {
    setPatientName(v)
    setNameErr(validatePatientName(v))
  }

  const handleSubmit = async () => {
    if (!file) { setError('Please select a PDF file first.'); return }
    const ne = validatePatientName(patientName)
    if (ne) { setNameErr(ne); return }
    setLoading(true); setError('')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('lang', lang)
    if (patientName.trim()) formData.append('patient_name', patientName.trim())
    try {
      const data = await api.analyse(formData)
      onResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-page">
      {/* Hero */}
      <div className="hero animate-fade-in-up">
        <div className="hero-badge"><ShieldCheck size={13} /><span>AI-Powered Medical Report Analysis</span></div>
        <h1 className="hero-title">
          {t.heroTitle1}<br /><span className="hero-gradient">{t.heroTitle2}</span>
        </h1>
        <p className="hero-subtitle">{t.heroSub}</p>
        <div className="feature-pills">
          <div className="pill"><Zap size={13} /><span>Instant Analysis</span></div>
          <div className="pill"><Brain size={13} /><span>AI Powered</span></div>
          <div className="pill"><ShieldCheck size={13} /><span>Private & Secure</span></div>
        </div>
      </div>

      {/* Upload card */}
      <div className="upload-card animate-scale-in">

        {/* Patient name */}
        <div className="form-group">
          <label className="form-label">
            <User size={14} />{t.patientName}
            <span className="optional">{t.optional}</span>
          </label>
          <input
            className={`form-input ${nameErr ? 'input-error' : ''}`}
            type="text"
            placeholder="e.g. Bhagyesh Shah"
            value={patientName}
            onChange={e => handleNameChange(e.target.value)}
          />
          {nameErr && <span className="input-err-msg">{nameErr}</span>}
        </div>

        {/* PDF drop zone */}
        <div className="form-group">
          <label className="form-label"><FileText size={14} />Lab Report PDF</label>
          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
            onClick={() => !file && inputRef.current.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <input ref={inputRef} type="file" accept=".pdf" style={{ display:'none' }}
              onChange={e => handleFile(e.target.files[0])} />
            {file ? (
              <div className="file-selected">
                <div className="file-icon-wrap"><FileText size={22} /></div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">{(file.size/1024).toFixed(1)} KB</div>
                </div>
                <button className="file-remove" onClick={e => { e.stopPropagation(); setFile(null) }}>
                  <X size={15} />
                </button>
              </div>
            ) : (
              <div className="drop-placeholder">
                <div className="drop-icon-wrap"><Upload size={26} /></div>
                <div className="drop-text">{t.dropText}</div>
                <div className="drop-hint">{t.dropHint}</div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="error-msg animate-fade-in">
            <ShieldCheck size={15} />{error}
          </div>
        )}

        <button
          className={`analyse-btn ${loading ? 'loading' : ''}`}
          onClick={handleSubmit}
          disabled={loading || !file || !!nameErr}
        >
          {loading
            ? <><Loader2 size={18} className="spin-icon" /><span>{t.analysing}</span></>
            : <><Brain size={18} /><span>{t.analyseBtn}</span><ArrowRight size={16} className="btn-arrow" /></>
          }
        </button>

        {loading && <div className="loading-bar-wrap"><div className="loading-bar" /></div>}
      </div>

      {/* How it works */}
      <div className="how-section animate-fade-in-up">
        <h3 className="how-title">{t.howWorks}</h3>
        <div className="steps-grid">
          {[
            { Icon: Upload,      num:'01', title:'Upload PDF',     desc:'Drop your lab report PDF — digital or scanned' },
            { Icon: Brain,       num:'02', title:'AI Analysis',    desc:'AI reads every test value and reference range' },
            { Icon: ShieldCheck, num:'03', title:'Plain Language', desc:'Get colour-coded results with clear explanations' },
          ].map(({ Icon, num, title, desc }, i) => (
            <div className="step-card" key={i} style={{ animationDelay:`${i*0.1}s` }}>
              <div className="step-num">{num}</div>
              <div className="step-icon"><Icon size={20} /></div>
              <div className="step-title">{title}</div>
              <div className="step-desc">{desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="disclaimer animate-fade-in">
        <ShieldCheck size={15} />
        <span><strong>Medical Disclaimer:</strong> {t.disclaimer}</span>
      </div>
    </div>
  )
}
