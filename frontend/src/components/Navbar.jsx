import { useState, useEffect } from 'react'
import { Upload, Clock, GitCompare, Activity, Menu, X, LogOut, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useLang, LANGS } from '../context/LangContext'
import './Navbar.css'

export default function Navbar({ page, goTo }) {
  const { user, logout } = useAuth()
  const { lang, switchLang, t } = useLang()
  const [scrolled,  setScrolled]  = useState(false)
  const [menuOpen,  setMenuOpen]  = useState(false)
  const [userMenu,  setUserMenu]  = useState(false)

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 10)
    window.addEventListener('scroll', fn)
    return () => window.removeEventListener('scroll', fn)
  }, [])

  const nav = (p) => { goTo(p); setMenuOpen(false); setUserMenu(false) }

  const navItems = [
    { key: 'upload',  label: t.upload,  Icon: Upload },
    { key: 'history', label: t.history, Icon: Clock },
    { key: 'compare', label: t.compare, Icon: GitCompare },
  ]

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="navbar-inner">

        {/* Logo */}
        <div className="navbar-brand" onClick={() => nav('upload')}>
          <div className="logo-wrap">
            <div className="logo-ring" />
            <div className="logo-icon"><Activity size={18} strokeWidth={2.5} /></div>
          </div>
          <div className="brand-text">
            <span className="brand-name">MedEasy</span>
            <span className="brand-tagline">Report Simplifier</span>
          </div>
        </div>

        {/* Desktop nav */}
        <div className="navbar-center desktop-only">
          {navItems.map(({ key, label, Icon }) => (
            <button
              key={key}
              className={`nav-btn ${page === key ? 'active' : ''}`}
              onClick={() => nav(key)}
            >
              <Icon size={14} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Right side */}
        <div className="navbar-right desktop-only">
          {/* Language toggle */}
          <div className="lang-toggle">
            {Object.entries(LANGS).map(([code, { label }]) => (
              <button
                key={code}
                className={`lang-btn ${lang === code ? 'active' : ''}`}
                onClick={() => switchLang(code)}
                title={LANGS[code].full}
              >
                {label}
              </button>
            ))}
          </div>

          {/* User menu */}
          <div className="user-menu-wrap">
            <button className="user-btn" onClick={() => setUserMenu(v => !v)}>
              <div className="user-avatar">{user?.name?.[0]?.toUpperCase() || 'U'}</div>
              <span className="user-name">{user?.name?.split(' ')[0]}</span>
            </button>
            {userMenu && (
              <div className="user-dropdown animate-fade-in">
                <div className="user-dropdown-info">
                  <div className="user-dropdown-name">{user?.name}</div>
                  <div className="user-dropdown-email">{user?.email}</div>
                </div>
                <hr className="dropdown-divider" />
                <button className="dropdown-item danger" onClick={logout}>
                  <LogOut size={14} /> {t.logout}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile hamburger */}
        <button className="hamburger mobile-only" onClick={() => setMenuOpen(v => !v)}>
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="mobile-menu animate-fade-in">
          {navItems.map(({ key, label, Icon }) => (
            <button
              key={key}
              className={`mobile-nav-btn ${page === key ? 'active' : ''}`}
              onClick={() => nav(key)}
            >
              <Icon size={16} /> {label}
            </button>
          ))}
          <div className="mobile-lang-row">
            {Object.entries(LANGS).map(([code, { full }]) => (
              <button
                key={code}
                className={`lang-btn ${lang === code ? 'active' : ''}`}
                onClick={() => switchLang(code)}
              >
                {full}
              </button>
            ))}
          </div>
          <button className="mobile-nav-btn danger" onClick={logout}>
            <LogOut size={16} /> {t.logout}
          </button>
        </div>
      )}
    </nav>
  )
}
