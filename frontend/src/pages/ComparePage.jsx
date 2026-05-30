import { useState, useEffect } from 'react'
import { ArrowLeft, GitCompare, TrendingUp, TrendingDown, Minus, Plus, Loader2, AlertTriangle } from 'lucide-react'
import { useLang } from '../context/LangContext'
import { api } from '../api'
import './ComparePage.css'

const CHANGE_CONFIG = {
  improved: { cls: 'improved', Icon: TrendingDown,  label: 'Improved' },
  worsened: { cls: 'worsened', Icon: TrendingUp,    label: 'Worsened' },
  stable:   { cls: 'stable',   Icon: Minus,         label: 'Stable'   },
  new:      { cls: 'new',      Icon: Plus,          label: 'New'      },
}

export default function ComparePage({ onBack }) {
  const { lang, t } = useLang()
  const [reports,   setReports]   = useState([])
  const [reportA,   setReportA]   = useState('')
  const [reportB,   setReportB]   = useState('')
  const [loading,   setLoading]   = useState(false)
  const [fetching,  setFetching]  = useState(true)
  const [result,    setResult]    = useState(null)
  const [error,     setError]     = useState('')

  useEffect(() => {
    api.getReports()
      .then(data => setReports(data))
      .catch(err => setError(err.message))
      .finally(() => setFetching(false))
  }, [])

  const handleCompare = async () => {
    if (!reportA || !reportB) { setError('Please select two reports.'); return }
    if (reportA === reportB)  { setError('Please select two different reports.'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const data = await api.compare(Number(reportA), Number(reportB), lang)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const improved = result?.changes?.filter(c => c.change === 'improved') || []
  const worsened = result?.changes?.filter(c => c.change === 'worsened') || []
  const stable   = result?.changes?.filter(c => c.change === 'stable')   || []
  const newTests = result?.changes?.filter(c => c.change === 'new')      || []

  return (
    <div className="compare-page">
      <button className="back-btn animate-slide-left" onClick={onBack}>
        <ArrowLeft size={16} /><span>Back</span>
      </button>

      <div className="compare-header animate-fade-in-up">
        <div className="compare-header-icon"><GitCompare size={22} /></div>
        <div>
          <h2 className="compare-title">{t.compareReports}</h2>
          <p className="compare-sub">{t.selectTwo}</p>
        </div>
      </div>

      {/* Selector */}
      <div className="compare-selectors animate-scale-in">
        <div className="selector-group">
          <label className="selector-label">Report A <span className="selector-hint">(older)</span></label>
          <select className="selector-input" value={reportA} onChange={e => setReportA(e.target.value)}>
            <option value="">{t.selectReport}</option>
            {reports.map(r => (
              <option key={r.id} value={r.id}>
                {r.patient_name ? `${r.patient_name} — ` : ''}{r.filename} ({new Date(r.uploaded_at).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>

        <div className="compare-vs">
          <GitCompare size={20} />
        </div>

        <div className="selector-group">
          <label className="selector-label">Report B <span className="selector-hint">(newer)</span></label>
          <select className="selector-input" value={reportB} onChange={e => setReportB(e.target.value)}>
            <option value="">{t.selectReport}</option>
            {reports.map(r => (
              <option key={r.id} value={r.id}>
                {r.patient_name ? `${r.patient_name} — ` : ''}{r.filename} ({new Date(r.uploaded_at).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="compare-error animate-fade-in">
          <AlertTriangle size={15} />{error}
        </div>
      )}

      <button className="compare-btn" onClick={handleCompare} disabled={loading || !reportA || !reportB}>
        {loading
          ? <><Loader2 size={17} className="spin-icon" />Comparing...</>
          : <><GitCompare size={17} />{t.compareBtn}</>
        }
      </button>

      {/* Results */}
      {result && (
        <div className="compare-results animate-fade-in-up">
          {/* Report labels */}
          <div className="compare-labels">
            <div className="compare-label-a">
              <span className="label-dot a" />
              <div>
                <div className="label-name">Report A</div>
                <div className="label-file">{result.report_a.filename}</div>
              </div>
            </div>
            <div className="compare-label-b">
              <span className="label-dot b" />
              <div>
                <div className="label-name">Report B</div>
                <div className="label-file">{result.report_b.filename}</div>
              </div>
            </div>
          </div>

          {/* Summary pills */}
          <div className="compare-summary-pills">
            {[
              { count: improved.length, label: t.improved, cls: 'improved' },
              { count: worsened.length, label: t.worsened, cls: 'worsened' },
              { count: stable.length,   label: t.stable,   cls: 'stable'   },
              { count: newTests.length, label: t.new,      cls: 'new'      },
            ].map(({ count, label, cls }) => (
              <div key={cls} className={`summary-pill ${cls}`}>
                <span className="pill-num">{count}</span>
                <span className="pill-label">{label}</span>
              </div>
            ))}
          </div>

          {/* Change groups */}
          {[
            { items: worsened, title: t.worsened, cls: 'worsened' },
            { items: improved, title: t.improved, cls: 'improved' },
            { items: newTests, title: t.new,      cls: 'new'      },
            { items: stable,   title: t.stable,   cls: 'stable'   },
          ].filter(g => g.items.length > 0).map(({ items, title, cls }) => (
            <div key={cls} className="change-group">
              <div className={`change-group-header ${cls}`}>
                {CHANGE_CONFIG[cls]?.Icon && (() => { const I = CHANGE_CONFIG[cls].Icon; return <I size={15} /> })()}
                <span>{title}</span>
                <span className="change-count">{items.length}</span>
              </div>
              {items.map((c, i) => (
                <div key={i} className={`change-card ${cls} animate-fade-in-up`}
                  style={{ animationDelay:`${i*0.05}s` }}>
                  <div className="change-card-header">
                    <span className="change-test">{c.test}</span>
                    <div className="change-values">
                      <span className="change-old">{c.old_value || '—'}</span>
                      <span className="change-arrow">→</span>
                      <span className="change-new">{c.new_value || '—'}</span>
                    </div>
                  </div>
                  {c.note && <p className="change-note">{c.note}</p>}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
