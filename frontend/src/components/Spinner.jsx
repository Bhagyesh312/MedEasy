import './Spinner.css'

export default function Spinner({ size = 20, color = 'var(--primary)' }) {
  return (
    <div
      className="spinner"
      style={{ width: size, height: size, borderTopColor: color }}
    />
  )
}
