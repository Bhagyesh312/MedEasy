import { useState } from 'react'
import { Activity, Mail, Lock, User, Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useLang, LANGS } from '../context/LangContext'
import { api } from '../api'
import './AuthPage.css'

// ── Validation helpers ────────────────────────────────────────────────────────
function validateName(v) {
  if (!v.trim()) return 'Name is required.'
  if (v.trim().length < 2) return 'Name must be at least 2 characters.'
  if (v.trim().length > 50) return 'Name must be 50 characters or fewer.'
  if (/[0-9]/.test(v)) return 'Name cannot contain numbers.'
  if (/[^A-Za-z\u0900-\u097F\u0A80-\u0AFF\s\-'.]/.test(v))
    return 'Name can only contain letters, spaces, hyphens and dots.'
  return ''
}

function validateEmail(v) {
  if (!v.trim()) return 'Email is required.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'Please enter a valid email address.'
  return ''
}

function validatePassword(v) {
  if (!v) return 'Password is required.'
  if (v.length < 8) return 'Password must be at least 8 characters.'
  if (!/[0-9]/.test(v)) return 'Password must contain at least one number.'
  if (!/[A-Za-z]/.test(v)) return 'Password must contain at least one letter.'
  return ''
}

function passwordStrength(v) {
  if (!v) return { score: 0, label: '', color: '' }
  let score = 0
  if (v.length >= 8)  score++
  if (v.length >= 12) score++
  if (/[0-9]/.test(v)) score++
  if (/[A-Z]/.test(v)) score++
  if (/[^A-Za-z0-9]/.test(v)) score++
  if (score <= 1) return { score, label: 'Weak',   color: '#b91c1c' }
  if (score <= 3) return { score, label: 'Fair',   color: '#c2410c' }
  if (score === 4) return { score, label: 'Good',   color: '#0f766e' }
  return              { score, label: 'Strong', color: '#15803d' }
}

export default function AuthPage() {
  const { login }               = useAuth()
  const { lang, switchLang, t } = useLang()

  const [mode,     setMode]     = useState('login')
  const [name,     setName]     = useState('')
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [showPw,   setShowPw]   = useState(false)
  const [showCf,   setShowCf]   = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

  const [nameErr,    setNameErr]    = useState('')
  const [emailErr,   setEmailErr]   = useState('')
  const [pwErr,      setPwErr]      = useState('')
  const [confirmErr, setConfirmErr] = useState('')

  const pwStrength = passwordStrength(password)

  const clearErrors = () => {
    setError('')
    setNameErr(''); setEmailErr(''); setPwErr(''); setConfirmErr('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearErrors()

    if (mode === 'login') {
      const ee = validateEmail(email)
      if (ee) { setEmailErr(ee); return }
      if (!password) { setPwErr('Password is required.'); return }
      setLoading(true)
      try {
        const data = await api.login(email, password)
        login(data.user, data.token)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    } else {
      const ne = validateName(name)
      const ee = validateEmail(email)
      const pe = validatePassword(password)
      if (ne) { setNameErr(ne); return }
      if (ee) { setEmailErr(ee); return }
      if (pe) { setPwErr(pe); return }
      if (!confirm) { setConfirmErr('Please confirm your password.'); return }
      if (password !== confirm) { setConfirmErr('Passwords do not match.'); return }
      setLoading(true)
      try {
        const data = await api.register(name, email, password)
        login(data.user, data.token)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
  }

  const switchMode = () => {
    setMode(m => m === 'login' ? 'register' : 'login')
    clearErrors()
    setName(''); setEmail(''); setPassword(''); setConfirm('')
  }

  return (
    <div className="auth-page">
      {/* Left branding panel */}
      <div className="auth-left">
        <div className="auth-left-logo">
          <div className="auth-left-logo-box"><Activity size={18} /></div>
          <span className="auth-left-brand">MedEasy</span>
        </div>
        <div>
          <p className="auth-left-tagline">Understand your lab report in plain language</p>
          <p className="auth-left-sub">
            Upload any medical report and get a clear explanation — no medical background needed.
            Available in English, Hindi and Gujarati.
          </p>
        </div>
        <p className="auth-left-footer">MedEasy · Medical Report Simplifier</p>
      </div>

      {/* Right form panel */}
      <div className="auth-right">
        <div className="auth-card animate-fade-in">

          {/* Mobile logo */}
          <div className="auth-logo">
            <div className="auth-logo-ring">
              <div className="auth-logo-icon"><Activity size={18} /></div>
            </div>
            <div className="auth-brand">MedEasy</div>
          </div>

          <h2 className="auth-title">
            {mode === 'login' ? t.loginTitle : t.registerTitle}
          </h2>
          <p className="auth-sub">
            {mode === 'login'
              ? 'Sign in to access your reports'
              : 'Create your free account to get started'}
          </p>

          {/* Language toggle */}
          <div className="auth-lang">
            {Object.entries(LANGS).map(([code, { full }]) => (
              <button
                key={code}
                className={`auth-lang-btn ${lang === code ? 'active' : ''}`}
                onClick={() => switchLang(code)}
              >
                {full}
              </button>
            ))}
          </div>

          {error && <div className="auth-error animate-fade-in">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit}>

            {/* Name — register only */}
            {mode === 'register' && (
              <div className="field">
                <label className="field-label"><User size={12} />{t.name}</label>
                <input
                  className={`field-input ${nameErr ? 'field-error' : ''}`}
                  type="text"
                  placeholder="Bhagyesh Shah"
                  value={name}
                  onChange={e => { setName(e.target.value); setNameErr('') }}
                  autoComplete="name"
                />
                {nameErr && <span className="field-err-msg">{nameErr}</span>}
              </div>
            )}

            {/* Email */}
            <div className="field">
              <label className="field-label"><Mail size={12} />{t.email}</label>
              <input
                className={`field-input ${emailErr ? 'field-error' : ''}`}
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => { setEmail(e.target.value); setEmailErr('') }}
                autoComplete="email"
              />
              {emailErr && <span className="field-err-msg">{emailErr}</span>}
            </div>

            {/* Password */}
            <div className="field">
              <label className="field-label"><Lock size={12} />{t.password}</label>
              <div className="pw-wrap">
                <input
                  className={`field-input ${pwErr ? 'field-error' : ''}`}
                  type={showPw ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => { setPassword(e.target.value); setPwErr('') }}
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                />
                <button type="button" className="pw-toggle" onClick={() => setShowPw(v => !v)}>
                  {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {pwErr && <span className="field-err-msg">{pwErr}</span>}

              {/* Password strength — register only */}
              {mode === 'register' && password && (
                <div className="pw-strength">
                  <div className="pw-strength-bar">
                    {[1,2,3,4,5].map(i => (
                      <div
                        key={i}
                        className="pw-strength-seg"
                        style={{ background: i <= pwStrength.score ? pwStrength.color : '#e7e5e4' }}
                      />
                    ))}
                  </div>
                  <span className="pw-strength-label" style={{ color: pwStrength.color }}>
                    {pwStrength.label}
                  </span>
                </div>
              )}
            </div>

            {/* Confirm password — register only */}
            {mode === 'register' && (
              <div className="field">
                <label className="field-label"><Lock size={12} />Confirm Password</label>
                <div className="pw-wrap">
                  <input
                    className={`field-input ${confirmErr ? 'field-error' : ''}`}
                    type={showCf ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={confirm}
                    onChange={e => { setConfirm(e.target.value); setConfirmErr('') }}
                    autoComplete="new-password"
                  />
                  <button type="button" className="pw-toggle" onClick={() => setShowCf(v => !v)}>
                    {showCf ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {confirmErr && <span className="field-err-msg">{confirmErr}</span>}
                {confirm && (
                  <span className="field-err-msg" style={{ color: confirm === password ? 'var(--green)' : 'var(--red)' }}>
                    {confirm === password ? '✓ Passwords match' : '✗ Passwords do not match'}
                  </span>
                )}
              </div>
            )}

            <button className="auth-submit" type="submit" disabled={loading}>
              {loading
                ? <><Loader2 size={16} className="spin-icon" /> Loading...</>
                : mode === 'login' ? t.loginBtn : t.registerBtn
              }
            </button>
          </form>

          <div className="auth-switch">
            {mode === 'login' ? t.noAccount : t.hasAccount}
            <button className="auth-switch-btn" onClick={switchMode}>
              {mode === 'login' ? t.signUp : t.signIn}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
