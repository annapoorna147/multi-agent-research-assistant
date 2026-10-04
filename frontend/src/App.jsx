import { useState } from "react";
import "./App.css";
import Workspace from "./Workspace";

function App() {
  const [showWorkspace, setShowWorkspace] = useState(false);

  if (showWorkspace) {
    return <Workspace />;
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <span>Research AI</span>
        </div>

        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#agents">Agents</a>
          <a href="#about">About</a>
        </div>

        <button
          className="nav-button"
          onClick={() => setShowWorkspace(true)}
        >
          Open Workspace
        </button>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-badge">
            <span className="status-dot" />
            Multi-Agent Intelligence
          </div>

          <h1>
            Research smarter.
            <br />
            <span>Discover deeper.</span>
          </h1>

          <p className="hero-text">
            An AI-powered research platform that searches the web,
            verifies information, analyzes sources, and builds
            evidence-backed reports using specialized AI agents.
          </p>

          <div className="research-box">
            <textarea
              placeholder="What would you like to research?"
              rows="3"
            />

            <div className="research-controls">
              <div className="mode-buttons">
                <button className="mode active">Quick</button>
                <button className="mode">Standard</button>
                <button className="mode">Deep</button>
              </div>

              <button
                className="start-button"
                onClick={() => setShowWorkspace(true)}
              >
                Start Research
                <span>→</span>
              </button>
            </div>
          </div>

          <div className="hero-note">
            Search · Verify · Analyze · Synthesize
          </div>
        </section>

        <section className="stats">
          <div>
            <strong>6+</strong>
            <span>AI Agents</span>
          </div>

          <div>
            <strong>Multi-source</strong>
            <span>Research</span>
          </div>

          <div>
            <strong>Evidence</strong>
            <span>Based Reports</span>
          </div>

          <div>
            <strong>Real-time</strong>
            <span>Web Discovery</span>
          </div>
        </section>

        <section id="features" className="section">
          <div className="section-heading">
            <span>CAPABILITIES</span>

            <h2>Research built like a team.</h2>

            <p>
              Instead of relying on a single AI response, Research AI
              divides complex research into specialized tasks.
            </p>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <div className="feature-icon">⌕</div>
              <h3>Web Discovery</h3>
              <p>
                Find relevant sources across the web and build a
                research collection around your question.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon">✓</div>
              <h3>Fact Checking</h3>
              <p>
                Evaluate claims against collected sources instead
                of blindly trusting generated information.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon">◈</div>
              <h3>Cross-Source Analysis</h3>
              <p>
                Compare evidence, identify patterns, and surface
                agreements and contradictions between sources.
              </p>
            </article>

            <article className="feature-card">
              <div className="feature-icon">✦</div>
              <h3>AI Synthesis</h3>
              <p>
                Turn the research process into a structured report
                that is easier to understand and use.
              </p>
            </article>
          </div>
        </section>

        <section id="agents" className="section agents-section">
          <div className="section-heading">
            <span>THE RESEARCH ENGINE</span>

            <h2>A team of specialized agents.</h2>

            <p>
              Each agent has a focused responsibility. Together
              they create a deeper research workflow.
            </p>
          </div>

          <div className="agent-flow">
            <div className="agent-card">
              <span>01</span>
              <strong>Researcher</strong>
              <small>Finds information</small>
            </div>

            <div className="flow-arrow">→</div>

            <div className="agent-card">
              <span>02</span>
              <strong>Fact Checker</strong>
              <small>Verifies claims</small>
            </div>

            <div className="flow-arrow">→</div>

            <div className="agent-card">
              <span>03</span>
              <strong>Analyst</strong>
              <small>Connects evidence</small>
            </div>

            <div className="flow-arrow">→</div>

            <div className="agent-card">
              <span>04</span>
              <strong>Synthesizer</strong>
              <small>Builds the report</small>
            </div>
          </div>
        </section>

        <section id="about" className="about-section">
          <div>
            <span className="section-label">BUILT WITH PURPOSE</span>

            <h2>Research should feel intelligent.</h2>
          </div>

          <p>
            Research AI is being built as a full research workspace
            where discovery, verification, analysis, and synthesis
            work together in one system.
          </p>
        </section>
      </main>

      <footer>
        <div>
          <strong>Research AI</strong>
          <span>Multi-Agent Research Assistant V2</span>
        </div>

        <div>
          <strong>Created & Developed by Annapoorna S U</strong>
        </div>
      </footer>
    </div>
  );
}

export default App;