
import { useState } from "react";
import "./Workspace.css";
import ResearchResults from "./ResearchResults";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

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
    { name: "Quick", description: "Fast overview" },
    { name: "Standard", description: "Balanced research" },
    { name: "Deep", description: "Maximum investigation" },
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
        `${API_BASE_URL}/api/research/`,
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

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.error ||
            `Research request failed (HTTP ${response.status}).`
        );
      }

      setResearchResult(data);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Unable to connect to the research service. Please try again."
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
        <section className="workspace-intro">
          <p className="workspace-eyebrow">MULTI-AGENT RESEARCH</p>
          <h1>What do you want to understand?</h1>
          <p>
            Ask a question. Research AI will investigate sources,
            examine evidence, and build a structured report.
          </p>
        </section>

        <section className="research-composer">
          <label htmlFor="research-question">
            Your research question
          </label>

          <textarea
            id="research-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: How is AI changing healthcare, and what are its limitations?"
            rows={5}
            disabled={isResearching}
          />

          <div className="research-mode-heading">Research depth</div>

          <div className="research-modes">
            {researchModes.map((researchMode) => (
              <button
                key={researchMode.name}
                type="button"
                className={
                  mode === researchMode.name
                    ? "research-mode active"
                    : "research-mode"
                }
                onClick={() => setMode(researchMode.name)}
                disabled={isResearching}
              >
                <strong>{researchMode.name}</strong>
                <span>{researchMode.description}</span>
              </button>
            ))}
          </div>

          <div className="research-submit-row">
            <span className="research-privacy-note">
              Verify important findings against their original sources.
            </span>

            <button
              type="button"
              className="start-research-button"
              onClick={handleStartResearch}
              disabled={!question.trim() || isResearching}
            >
              {isResearching ? "Researching..." : "Start Research →"}
            </button>
          </div>

          {isResearching && (
            <p className="research-progress" role="status">
              Research is in progress. This may take a little time.
            </p>
          )}

          {error && (
            <div className="research-error" role="alert">
              <strong>Research request failed</strong>
              <p>{error}</p>
              <button
                type="button"
                onClick={handleStartResearch}
                disabled={isResearching || !question.trim()}
              >
                Try again
              </button>
            </div>
          )}
        </section>

        {!researchResult && (
          <section className="agent-overview">
            <div className="agent-overview-heading">
              <h2>Your research team</h2>
              <p>Four specialist roles support the research process.</p>
            </div>

            <div className="agent-grid">
              {agents.map((agent) => (
                <article className="agent-card" key={agent.name}>
                  <div className="agent-icon" aria-hidden="true">
                    {agent.icon}
                  </div>
                  <h3>{agent.name}</h3>
                  <p>{agent.description}</p>
                </article>
              ))}
            </div>
          </section>
        )}

        {researchResult && (
          <ResearchResults result={researchResult} />
        )}
      </main>
    </div>
  );
}

export default Workspace;
