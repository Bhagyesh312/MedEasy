import { FileQuestion, ArrowLeft } from 'lucide-react'
import './NotFoundPage.css'

export default function NotFoundPage({ onBack }) {
  return (
    <div className="notfound-page">
      <div className="notfound-icon">
        <FileQuestion size={40} />
      </div>
      <h2 className="notfound-title">Page not found</h2>
      <p className="notfound-sub">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <button className="notfound-btn" onClick={onBack}>
        <ArrowLeft size={15} />
        Go back home
      </button>
    </div>
  )
}
