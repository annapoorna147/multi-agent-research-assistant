function ResearchResults({ result }) {
  if (!result) {
    return null;
  }

  const data = result.result || {};

  const bestSources = data.best_sources || [];
  const evidence = data.evidence || {};
  const contradictions = data.contradictions || {};
  const factChecking = data.fact_checking || {};
  const analysis = data.analysis || {};
  const finalReport = data.final_report || "";

  const evidenceSummary = evidence.summary || {};
  const contradictionSummary = contradictions.summary || {};

  return (
    <section className="research-results">
      <div className="results-header">
        <div>
          <span className="section-label">RESEARCH COMPLETE</span>

          <h2>Research results</h2>

          <p>
            Your research has been searched, evaluated, fact-checked,
            analyzed, and synthesized.
          </p>
        </div>

        <div className="results-status">
          <span className="status-dot"></span>
          {result.status || "completed"}
        </div>
      </div>

      <div className="result-question">
        <span>RESEARCH QUESTION</span>
        <h3>{result.question}</h3>
      </div>

      <div className="results-overview">
        <div className="result-stat">
          <span>BEST SOURCES</span>
          <strong>{bestSources.length}</strong>
        </div>

        <div className="result-stat">
          <span>CLAIMS ANALYZED</span>
          <strong>
            {evidenceSummary.total_claims ?? 0}
          </strong>
        </div>

        <div className="result-stat">
          <span>SUPPORTED</span>
          <strong>
            {evidenceSummary.supported_claims ?? 0}
          </strong>
        </div>

        <div className="result-stat">
          <span>CONTRADICTIONS</span>
          <strong>
            {contradictionSummary.contradictions ?? 0}
          </strong>
        </div>
      </div>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">✦</div>

          <div>
            <h3>Final Research Report</h3>

            <p>
              AI-generated synthesis based on the researched evidence.
            </p>
          </div>
        </div>

        <div className="final-report">
          {finalReport ? (
            <pre>{finalReport}</pre>
          ) : (
            <p>No final report was returned.</p>
          )}
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">◈</div>

          <div>
            <h3>Best Sources</h3>

            <p>
              Sources selected by the source intelligence system.
            </p>
          </div>
        </div>

        <div className="best-sources-list">
          {bestSources.length > 0 ? (
            bestSources.map((source, index) => (
              <article
                className="source-card"
                key={`${source.url || source.title}-${index}`}
              >
                <div className="source-rank">
                  #{source.rank || index + 1}
                </div>

                <div className="source-content">
                  <h4>
                    {source.title || "Untitled source"}
                  </h4>

                  <span className="source-domain">
                    {source.domain || source.url || "Unknown source"}
                  </span>

                  <p>
                    {source.snippet ||
                      source.text?.slice(0, 280) ||
                      "No source description available."}
                  </p>

                  <div className="source-meta">
                    <span>
                      Score:{" "}
                      {source.overall_score != null
                        ? source.overall_score.toFixed(1)
                        : "—"}
                    </span>

                    <span>
                      {source.recommendation ||
                        "Evaluated source"}
                    </span>
                  </div>
                </div>
              </article>
            ))
          ) : (
            <div className="empty-result">
              No best sources were returned.
            </div>
          )}
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">✓</div>

          <div>
            <h3>Evidence Intelligence</h3>

            <p>
              Claims were mapped against supporting research evidence.
            </p>
          </div>
        </div>

        <div className="evidence-summary">
          <div>
            <span>Support rate</span>
            <strong>
              {evidenceSummary.support_rate != null
                ? `${evidenceSummary.support_rate}%`
                : "—"}
            </strong>
          </div>

          <div>
            <span>Strong evidence</span>
            <strong>
              {evidenceSummary.strong ?? 0}
            </strong>
          </div>

          <div>
            <span>Weak evidence</span>
            <strong>
              {evidenceSummary.weak ?? 0}
            </strong>
          </div>

          <div>
            <span>Unsupported</span>
            <strong>
              {evidenceSummary.unsupported ?? 0}
            </strong>
          </div>
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">⚖</div>

          <div>
            <h3>Contradiction Analysis</h3>

            <p>
              The system checks whether important sources agree,
              disagree, or express uncertainty.
            </p>
          </div>
        </div>

        <div className="contradiction-panel">
          <div className="contradiction-status">
            <strong>
              {contradictionSummary.overall_status ||
                "No contradiction summary available"}
            </strong>

            <span>
              {contradictionSummary.contradictions ?? 0} contradictions
              {" · "}
              {contradictionSummary.uncertainties ?? 0} uncertainties
              {" · "}
              {contradictionSummary.agreements ?? 0} agreements
            </span>
          </div>
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">✓</div>

          <div>
            <h3>Fact Checking</h3>

            <p>
              Claims were evaluated against the collected source material.
            </p>
          </div>
        </div>

        <div className="analysis-card">
          <pre>
            {typeof factChecking === "string"
              ? factChecking
              : JSON.stringify(factChecking, null, 2)}
          </pre>
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div className="results-section-icon">◉</div>

          <div>
            <h3>Research Analysis</h3>

            <p>
              Cross-source analysis produced by the research analyst.
            </p>
          </div>
        </div>

        <div className="analysis-card">
          <pre>
            {typeof analysis === "string"
              ? analysis
              : JSON.stringify(analysis, null, 2)}
          </pre>
        </div>
      </section>
    </section>
  );
}

export default ResearchResults;