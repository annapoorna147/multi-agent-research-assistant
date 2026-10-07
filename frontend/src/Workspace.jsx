import { useState } from "react";
import "./Workspace.css";
import ResearchResults from "./ResearchResults";

function Workspace() {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState("Standard");

  const [isResearching, setIsResearching] = useState(false);
  const [researchResult, setResearchResult] = useState(null);
  const [error, setError] = useState("");

  const agents = [
    {
      name: "Researcher",
      description: "Finds relevant information and sources",
      icon: "⌕",
    },
    {
      name: "Fact Checker",
      description: "Verifies claims against evidence",
      icon: "✓",
    },
    {
      name: "Analyst",
      description: "Compares sources and identifies patterns",
      icon: "◈",
    },
    {
      name: "Synthesizer",
      description: "Builds the final research report",
      icon: "✦",
    },
  ];

  const researchModes = [
    {
      name: "Quick",
      description: "Fast overview",
    },
    {
      name: "Standard",
      description: "Balanced research",
    },
    {
      name: "Deep",
      description: "Maximum investigation",
    },
  ];

  const handleNewResearch = () => {
    setQuestion("");
    setMode("Standard");
    setResearchResult(null);
    setError("");
    setIsResearching(false);
  };

  const handleStartResearch = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isResearching) {
      return;
    }

    setIsResearching(true);
    setResearchResult(null);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/research/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
            mode,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Research request failed. Please try again."
        );
      }

      setResearchResult(data);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Unable to connect to the research service."
      );
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="workspace-page">
      <header className="workspace-header">
        <div className="workspace-brand">
          <div className="workspace-logo">R</div>

          <div>
            <strong>Research AI</strong>
            <span>Research Workspace</span>
          </div>
        </div>

        <button
          className="new-research-button"
          onClick={handleNewResearch}
          disabled={isResearching}
        >
          + New Research
        </button>
      </header>

      <main className="workspace-main">
        <aside className="workspace-sidebar">
          <div className="sidebar-section">
            <span className="sidebar-label">WORKSPACE</span>

            <button className="sidebar-item active">
              <span>⌕</span>
              Research
            </button>

            <button className="sidebar-item">
              <span>◷</span>
              History
            </button>

            <button className="sidebar-item">
              <span>▣</span>
              Saved Reports
            </button>
          </div>

          <div className="sidebar-section">
            <span className="sidebar-label">RESEARCH</span>

            <button className="sidebar-item">
              <span>⚙</span>
              Settings
            </button>
          </div>

          <div className="sidebar-user">
            <div className="user-avatar">A</div>

            <div>
              <strong>Annapoorna S U</strong>
              <span>Researcher</span>
            </div>
          </div>
        </aside>

        <section className="workspace-content">
          <div className="workspace-title">
            <span className="section-label">NEW RESEARCH</span>

            <h1>What would you like to discover?</h1>

            <p>
              Ask a question and let our specialized AI agents
              research, verify, analyze, and synthesize the answer.
            </p>
          </div>

          {!researchResult && (
            <>
              <div className="research-panel">
                <label htmlFor="research-question">
                  Research question
                </label>

                <textarea
                  id="research-question"
                  value={question}
                  onChange={(event) => {
                    setQuestion(event.target.value);
                    setError("");
                  }}
                  placeholder="Example: How will AI transform semiconductor manufacturing over the next five years?"
                  rows={6}
                  disabled={isResearching}
                />

                <div className="panel-footer">
                  <span>{question.length} characters</span>

                  <span>
                    Sources will be cited automatically
                  </span>
                </div>
              </div>

              <div className="mode-section">
                <div className="mode-heading">
                  <div>
                    <strong>Research mode</strong>

                    <span>
                      Choose how deeply the agents should investigate.
                    </span>
                  </div>
                </div>

                <div className="mode-grid">
                  {researchModes.map((item) => (
                    <button
                      key={item.name}
                      className={
                        mode === item.name
                          ? "mode-card selected"
                          : "mode-card"
                      }
                      onClick={() => setMode(item.name)}
                      disabled={isResearching}
                    >
                      <strong>{item.name}</strong>

                      <span>{item.description}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="agents-section">
                <div className="mode-heading">
                  <div>
                    <strong>AI research team</strong>

                    <span>
                      Multiple specialized agents collaborate on your
                      research.
                    </span>
                  </div>
                </div>

                <div className="agents-grid">
                  {agents.map((agent) => (
                    <div
                      className="workspace-agent"
                      key={agent.name}
                    >
                      <div className="agent-icon">
                        {agent.icon}
                      </div>

                      <div>
                        <strong>{agent.name}</strong>

                        <span>{agent.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <button
                className="workspace-start-button"
                onClick={handleStartResearch}
                disabled={!question.trim() || isResearching}
              >
                {isResearching
                  ? "Researching..."
                  : "Start Research"}

                <span>
                  {isResearching ? "…" : "→"}
                </span>
              </button>

              {error && (
                <div className="research-error">
                  <strong>Research failed</strong>

                  <span>{error}</span>
                </div>
              )}
            </>
          )}

          {researchResult && (
            <ResearchResults result={researchResult} />
          )}
        </section>
      </main>
    </div>
  );
}

export default Workspace;