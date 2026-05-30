import { useState } from 'react'
import {
  CheckCircle2, TrendingUp, TrendingDown, AlertOctagon,
  HelpCircle, ChevronDown, ChevronUp, Clock, ArrowRight,
  Activity, Stethoscope, Zap
} from 'lucide-react'
import './FindingCard.css'

const STATUS_CONFIG = {
  Normal:   { cls: 'normal',   Icon: CheckCircle2,  label: 'Normal'   },
  High:     { cls: 'high',     Icon: TrendingUp,    label: 'High'     },
  Low:      { cls: 'low',      Icon: TrendingDown,  label: 'Low'      },
  Critical: { cls: 'critical', Icon: AlertOctagon,  label: 'Critical' },
  Unknown:  { cls: 'unknown',  Icon: HelpCircle,    label: 'Unknown'  },
}

const URGENCY_CONFIG = {
  'Routine':          { color: 'var(--green)',  bg: 'var(--green-bg)'  },
  'Soon (1-2 weeks)': { color: 'var(--orange)', bg: 'var(--orange-bg)' },
  'Urgent (today)':   { color: 'var(--red)',    bg: 'var(--red-bg)'    },
}

export default function FindingCard({ finding, index = 0 }) {
  const [expanded, setExpanded] = useState(finding.flag)
  const cfg = STATUS_CONFIG[finding.status] || STATUS_CONFIG.Unknown
  const { Icon } = cfg
  const urgency = URGENCY_CONFIG[finding.urgency] || URGENCY_CONFIG['Routine']

  return (
    <div
      className={`finding-card ${cfg.cls}`}
      style={{ animationDelay: `${index * 0.06}s` }}
    >
      {/* ── Header (always visible) ── */}
      <div className="finding-header" onClick={() => setExpanded(v => !v)}>
        <div className="finding-icon-wrap">
          <Icon size={15} strokeWidth={2.5} />
        </div>
        <div className="finding-title-group">
          <span className="finding-name">{finding.test}</span>
          <span className="finding-value-inline">{finding.value}</span>
        </div>
        {finding.urgency && finding.urgency !== 'Routine' && (
          <span className="finding-urgency-badge" style={{ color: urgency.color, background: urgency.bg }}>
            <Clock size={10} />
            {finding.urgency}
          </span>
        )}
        <span className={`finding-badge ${cfg.cls}`}>{cfg.label}</span>
        <button className="finding-toggle">
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
      </div>

      {/* ── Expanded body ── */}
      {expanded && (
        <div className="finding-body animate-fade-in">

          {/* Reference range */}
          {finding.reference_range && finding.reference_range !== 'Not specified' && (
            <div className="finding-ref-row">
              <span className="finding-ref-label">Reference Range</span>
              <span className="finding-ref-value">{finding.reference_range}</span>
              {finding.your_number_context && (
                <span className="finding-context">{finding.your_number_context}</span>
              )}
            </div>
          )}

          {/* What it measures */}
          {finding.what_it_measures && (
            <div className="finding-detail-row">
              <div className="detail-icon"><Activity size={12} /></div>
              <span className="detail-text">{finding.what_it_measures}</span>
            </div>
          )}

          {/* Explanation */}
          {finding.explanation && (
            <p className="finding-explanation">{finding.explanation}</p>
          )}

          {/* Symptoms — only for flagged */}
          {finding.flag && finding.symptoms?.length > 0 && (
            <div className="finding-symptoms">
              <span className="symptoms-label">
                <Zap size={11} /> Possible symptoms
              </span>
              <div className="symptoms-list">
                {finding.symptoms.map((s, i) => (
                  <span key={i} className="symptom-tag">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Likely next step */}
          {finding.likely_next_step && (
            <div className="finding-detail-row next-step">
              <div className="detail-icon"><Stethoscope size={12} /></div>
              <span className="detail-text">{finding.likely_next_step}</span>
            </div>
          )}

          {/* Action */}
          {finding.action && (
            <div className="finding-action">
              <ArrowRight size={12} className="action-arrow" />
              <span>{finding.action}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
