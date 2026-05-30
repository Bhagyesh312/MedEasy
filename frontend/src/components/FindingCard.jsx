import { useState } from 'react'
import { CheckCircle2, TrendingUp, TrendingDown, AlertOctagon, HelpCircle, ChevronDown, ChevronUp } from 'lucide-react'
import './FindingCard.css'

const STATUS_CONFIG = {
  Normal:   { cls: 'normal',   Icon: CheckCircle2,   label: 'Normal' },
  High:     { cls: 'high',     Icon: TrendingUp,     label: 'High' },
  Low:      { cls: 'low',      Icon: TrendingDown,   label: 'Low' },
  Critical: { cls: 'critical', Icon: AlertOctagon,   label: 'Critical' },
  Unknown:  { cls: 'unknown',  Icon: HelpCircle,     label: 'Unknown' },
}

export default function FindingCard({ finding, index = 0 }) {
  const [expanded, setExpanded] = useState(finding.flag)
  const cfg = STATUS_CONFIG[finding.status] || STATUS_CONFIG.Unknown
  const { Icon } = cfg

  return (
    <div
      className={`finding-card ${cfg.cls}`}
      style={{ animationDelay: `${index * 0.06}s` }}
    >
      <div className="finding-header" onClick={() => setExpanded(v => !v)}>
        <div className="finding-icon-wrap">
          <Icon size={16} strokeWidth={2.5} />
        </div>
        <div className="finding-title-group">
          <span className="finding-name">{finding.test}</span>
          <span className="finding-value-inline">{finding.value}</span>
        </div>
        <span className={`finding-badge ${cfg.cls}`}>{cfg.label}</span>
        <button className="finding-toggle">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {expanded && (
        <div className="finding-body animate-fade-in">
          {finding.reference_range && finding.reference_range !== 'Not specified' && (
            <div className="finding-ref-row">
              <span className="finding-ref-label">Reference Range</span>
              <span className="finding-ref-value">{finding.reference_range}</span>
            </div>
          )}
          <p className="finding-explanation">{finding.explanation}</p>
          {finding.action && (
            <div className="finding-action">
              <div className="action-dot" />
              <span>{finding.action}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
