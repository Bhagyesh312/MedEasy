import { useState } from 'react'
import { Activity, Mail, Lock, User, Eye, EyeOff, ArrowRight, Loader2, ShieldCheck, RefreshCw } from 'lucide-react'
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
  if (/[^A-Za-z\u0900-\u097F\u0A80-\u0AFF\s\-'.]/.test(v)) return 'Name can only contain letters, spaces, hyphens and dots.'
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

// ── Component ─────────────────────────────────────────────────────────────────
export default function AuthPage() {
  const { login }          = useAuth()
  const { lang, switchLang, t } = useLang()

  // mode: 'login' | 'register' | 'otp'
  const [mode,     setMode]     = useState('login')
  const [name,     setName]     = useState('')
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [otp,      setOtp]      = useState('')
  const [showPw,   setShowPw]   = useState(false)
  const [showCf,   setShowCf]   = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [resending,setResending]= useState(false)
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')

  // Field-level errors
  const [nameErr,    setNameErr]    = useState('')
  const [emailErr,   setEmailErr]   = useState('')
  const [pwErr,      setPwErr]      = useState('')
  const [confirmErr, setConfirmErr] = useState('')
  const [otpErr,     setOtpErr]     = useState('')

  const pwStrength = passwordStrength(password)

  const clearErrors = () => {
    setError(''); setSuccess('')
    setNameErr(''); setEmailErr(''); setPwErr(''); setConfirmErr(''); setOtpErr('')
  }

  // ── Login ──────────────────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault()
    clearErrors()
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
  }

  // ── Register step 1: send OTP ──────────────────────────────────────────────
  const handleSendOtp = async (e) => {
    e.preventDefault()
    clearErrors()
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
      await api.sendOtp(name, email, password)
      setSuccess(`Verification code sent to ${email}`)
      setMode('otp')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ── Register step 2: verify OTP ───────────────────────────────────────────
  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    clearErrors()
    if (!otp.trim()) { setOtpErr('Please enter the verification code.'); return }
    if (!/^\d{6}$/.test(otp.trim())) { setOtpErr('Code must be exactly 6 digits.'); return }

    setLoading(true)
    try {
      const data = await api.register(name, email, password, otp.trim())
      login(data.user, data.token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ── Resend OTP ─────────────────────────────────────────────────────────────
  const handleResend = async () => {
    setResending(true); clearErrors()
    try {
      await api.sendOtp(name, email, password)
      setSuccess('New code sent to your email.')
      setOtp('')
    } catch (err) {
      setError(err.message)
    } finally {
      setResending(false)
    }
  }

  const switchToRegister = () => { setMode('register'); clearErrors(); setOtp(''); setConfirm('') }
  const switchToLogin    = () => { setMode('login');    clearErrors(); setOtp(''); setConfirm('') }

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

          {/* ── OTP step ── */}
          {mode === 'otp' ? (
            <>
              <div className="otp-header">
                <div className="otp-icon"><ShieldCheck size={22} /></div>
                <h2 className="auth-title">Check your email</h2>
                <p className="auth-sub">
                  We sent a 6-digit code to <strong>{email}</strong>.<br />
                  Enter it below to verify your account.
                </p>
              </div>

              {success && <div className="auth-success animate-fade-in">{success}</div>}
              {error   && <div className="auth-error   animate-fade-in">{error}</div>}

              <form className="auth-form" onSubmit={handleVerifyOtp}>
                <div className="field">
                  <label className="field-label">Verification Code</label>
                  <input
                    className={`field-input otp-input ${otpErr ? 'field-error' : ''}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    placeholder="000000"
                    value={otp}
                    onChange={e => { setOtp(e.target.value.replace(/\D/g, '')); setOtpErr('') }}
                    autoFocus
                    autoComplete="one-time-code"
                  />
                  {otpErr && <span className="field-err-msg">{otpErr}</span>}
                </div>

                <button className="auth-submit" type="submit" disabled={loading}>
                  {loading
                    ? <><Loader2 size={16} className="spin-icon" /> Verifying...</>
                    : <>Verify & Create Account</>
                  }
                </button>
              </form>

              <div className="otp-footer">
                <span>Didn't receive the code?</span>
                <button className="auth-switch-btn" onClick={handleResend} disabled={resending}>
                  {resending ? <><RefreshCw size={12} className="spin-icon" /> Sending...</> : 'Resend'}
                </button>
              </div>
              <div className="auth-switch" style={{ marginTop: 8 }}>
                <button className="auth-switch-btn" onClick={switchToLogin}>
                  ← Back to sign in
                </button>
              </div>
            </>
          ) : (
            <>
              <h2 className="auth-title">
                {mode === 'login' ? t.loginTitle : t.registerTitle}
              </h2>
              <p className="auth-sub">
                {mode === 'login'
                  ? 'Sign in to access your reports'
                  : 'Create your free account to get started'}
              </p>

              {/* Lang toggle */}
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

              {error   && <div className="auth-error   animate-fade-in">{error}</div>}
              {success && <div className="auth-success animate-fade-in">{success}</div>}

              <form className="auth-form" onSubmit={mode === 'login' ? handleLogin : handleSendOtp}>

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

                  {/* Password strength bar — register only */}
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
                    {/* Match indicator */}
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
                    : mode === 'login'
                      ? t.loginBtn
                      : 'Send Verification Code'
                  }
                </button>
              </form>

              <div className="auth-switch">
                {mode === 'login' ? t.noAccount : t.hasAccount}
                <button
                  className="auth-switch-btn"
                  onClick={mode === 'login' ? switchToRegister : switchToLogin}
                >
                  {mode === 'login' ? t.signUp : t.signIn}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
