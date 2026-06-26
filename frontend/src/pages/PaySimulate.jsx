import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { paymentApi } from '../api/services'

// Stand-in for the Paystack hosted checkout, used when the platform runs
// without live Paystack keys (simulation mode). It calls the verify endpoint,
// which finalizes the order, records commissions and dispatches notifications.
export default function PaySimulate() {
  const [params] = useSearchParams()
  const reference = params.get('reference')
  const navigate = useNavigate()
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  async function pay(outcome) {
    if (outcome === 'cancel') {
      navigate('/orders')
      return
    }
    setStatus('processing')
    setError('')
    try {
      await paymentApi.verify(reference)
      setStatus('done')
      setTimeout(() => navigate('/orders?paid=1'), 1200)
    } catch {
      setStatus('idle')
      setError('Payment verification failed. Please try again.')
    }
  }

  return (
    <div className="auth-wrap">
      <div className="pay-card">
        <div className="pay-brand">🔒 Secure Payment <span className="muted">(simulation)</span></div>
        <p className="muted">
          No live Paystack key is configured, so this page simulates the gateway so
          you can complete the full checkout flow.
        </p>
        <div className="pay-ref">Reference: <code>{reference}</code></div>

        {error && <div className="alert alert-error">{error}</div>}

        {status === 'done' ? (
          <div className="alert alert-success">✅ Payment successful! Redirecting…</div>
        ) : (
          <div className="pay-actions">
            <button className="btn btn-primary btn-block"
              disabled={status === 'processing'} onClick={() => pay('success')}>
              {status === 'processing' ? 'Processing…' : 'Pay now (approve)'}
            </button>
            <button className="btn btn-ghost btn-block"
              disabled={status === 'processing'} onClick={() => pay('cancel')}>
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
