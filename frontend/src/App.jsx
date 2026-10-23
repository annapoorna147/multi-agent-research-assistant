
import { useEffect, useState } from 'react'
import './App.css'

const modes = ['Quick', 'Standard', 'Deep']

function App() {
  const [question, setQuestion] = useState('')
  const [mode, setMode] = useState('Standard')
  const [apiStatus, setApiStatus] = useState('checking')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function checkBackend() {
      try {
        const response = await fetch('/api/health', {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error('Backend health check failed')
        }

        const data = await response.json()
        setApiStatus(data.status === 'healthy' ? 'connected' : 'offline')
      } catch (err) {
        if (err.name !== 'AbortError') {
          setApiStatus('offline')
        }
      }
    }

    checkBackend()
    return () => controller.abort()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()

    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || loading) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('/api/research/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          mode,
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail || `Research request failed (${response.status}).`
        )
      }

      setResult(data)
    } catch (err) {
      setError(
        err.message ||
          'Could not complete the request. Check that the backend is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Research AI home">
          <span className="brand-icon">R</span>
          <span>Research AI</span>
        </a>

        <div className={`connection ${apiStatus}`}>
          <span className="status-dot" />
          {apiStatus === 'checking'
            ? 'Checking backend…'
            : apiStatus === 'connected'
              ? 'Backend connected'
              : 'Backend unavailable'}
        </div>
      </header>

      <section className="hero">
        <div className="eyebrow">YOUR RESEARCH WORKSPACE</div>

        <h1>
          Research smarter.
          <br />
          <span>Think deeper.</span>
        </h1>

        <p className="subtitle">
          Turn research questions into structured research briefs.
          Explore a topic, organize key questions, and identify what
          needs evidence and verification.
        </p>

        <form className="research-panel" onSubmit={handleSubmit}>
          <label htmlFor="research-question">
            What would you like to research?
          </label>

          <textarea
            id="research-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="For example: What are the applications of AI in wireless communication?"
            rows={4}
            required
            disabled={loading}
          />

          <div className="panel-footer">
            <div className="mode-selector" aria-label="Research depth">
              {modes.map((item) => (
                <button
                  key={item}
                  type="button"
                  className={mode === item ? 'mode active' : 'mode'}
                  aria-pressed={mode === item}
                  onClick={() => setMode(item)}
                  disabled={loading}
                >
                  {item}
                </button>
              ))}
            </div>

            <button
              className="start-button"
              type="submit"
              disabled={!question.trim() || loading || apiStatus !== 'connected'}
            >
              {loading ? 'Preparing…' : 'Start Research'}
              {!loading && <span aria-hidden="true"> →</span>}
            </button>
          </div>

          <p className="form-note">
            {apiStatus !== 'connected'
              ? 'Waiting for the backend connection.'
              : 'This initial version creates a research brief, not a verified web research report.'}
          </p>
        </form>

        {loading && (
          <section className="result-panel" aria-live="polite">
            <h2>Preparing your research brief…</h2>
            <p>Please wait while the backend processes your question.</p>
          </section>
        )}

        {error && (
          <section className="result-panel error-panel" role="alert">
            <h2>Research request failed</h2>
            <p>{error}</p>
          </section>
        )}

        {result && (
          <section className="result-panel" aria-live="polite">
            <div className="eyebrow">RESEARCH BRIEF</div>
            <h2>{result.title || 'Your research brief'}</h2>

            <p>
              <strong>Question:</strong> {result.question || question}
            </p>

            <p>
              <strong>Mode:</strong> {result.mode || mode}
            </p>

            {result.summary && (
              <>
                <h3>Overview</h3>
                <p>{result.summary}</p>
              </>
            )}

            {Array.isArray(result.key_questions) &&
              result.key_questions.length > 0 && (
                <>
                  <h3>Questions to investigate</h3>
                  <ol>
                    {result.key_questions.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ol>
                </>
              )}

            {Array.isArray(result.next_steps) &&
              result.next_steps.length > 0 && (
                <>
                  <h3>Next steps</h3>
                  <ol>
                    {result.next_steps.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ol>
                </>
              )}

            <p className="form-note">
              {result.notice ||
                'This is a planning brief. Its points have not been independently verified.'}
            </p>
          </section>
        )}

        <div className="workflow">
          <div>
            <span>01</span>
            <strong>Discover</strong>
            <small>Identify research questions</small>
          </div>
          <div>
            <span>02</span>
            <strong>Verify</strong>
            <small>Find supporting evidence</small>
          </div>
          <div>
            <span>03</span>
            <strong>Analyze</strong>
            <small>Compare findings</small>
          </div>
          <div>
            <span>04</span>
            <strong>Synthesize</strong>
            <small>Build a report</small>
          </div>
        </div>
      </section>

      <footer>
        <span>Research AI</span>
        <span>Building reliable research, one step at a time.</span>
      </footer>
    </main>
  )
}

export default App
