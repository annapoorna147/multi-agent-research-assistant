import "./ResearchResults.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function MarkdownContent({ children }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ children, href, ...props }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
            {children}
          </a>
        ),
      }}
    >
      {typeof children === "string" ? children : ""}
    </ReactMarkdown>
  );
}

function MetricCard({ label, value, detail, icon }) {
  return (
    <article className="result-stat">
      <div className="metric-topline">
        <span>{label}</span>
        <span className="metric-icon">{icon}</span>
      </div>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function SectionHeading({ icon, title, description, count }) {
  return (
    <div className="results-section-heading">
      <div className="results-section-icon">{icon}</div>
      <div className="section-heading-copy">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      {count != null && <span className="section-count">{count}</span>}
    </div>
  );
}

function readable(value) {
  if (typeof value === "string") return value;
  if (value == null) return "";
  return JSON.stringify(value, null, 2);
}

export default function ResearchResults({ result }) {
  if (!result) return null;

  const data = result.result || {};
  const sources = data.best_sources || [];
  const evidence = data.evidence || {};
  const evidenceSummary = evidence.summary || {};
  const contradictionSummary = (data.contradictions || {}).summary || {};
  const coverage =
    evidenceSummary.evidence_coverage_rate ?? evidenceSummary.support_rate;
  const factChecking = readable(data.fact_checking);
  const analysis = readable(data.analysis);

  return (
    <section className="research-results" aria-label="Research results">
      <header className="results-header">
        <div>
          <span className="section-label">
            <span className="status-dot" /> RESEARCH COMPLETE
          </span>
          <h2>Your research, synthesized.</h2>
          <p>
            Explore the findings, inspect source material, and review the
            evidence behind your research.
          </p>
        </div>
        <span className="results-status">
          <span className="status-dot" />
          {result.status || "completed"}
        </span>
      </header>

      <div className="result-question">
        <span>YOUR RESEARCH QUESTION</span>
        <h3>{result.question || "Research question unavailable"}</h3>
      </div>

      <div className="results-overview">
        <MetricCard
          label="Sources selected"
          value={sources.length}
          detail="Ranked sources"
          icon="↗"
        />
        <MetricCard
          label="Claims analyzed"
          value={evidenceSummary.total_claims ?? 0}
          detail="Claims assessed"
          icon="◎"
        />
        <MetricCard
          label="Evidence coverage"
          value={coverage != null ? `${coverage}%` : "—"}
          detail="Relevance-based metric"
          icon="◈"
        />
        <MetricCard
          label="Contradictions"
          value={contradictionSummary.contradictions ?? 0}
          detail={`${contradictionSummary.uncertainties ?? 0} uncertainties`}
          icon="⚖"
        />
      </div>

      <section className="results-section report-section">
        <SectionHeading
          icon="✦"
          title="Final research report"
          description="The synthesized report generated from your research."
        />
        <div className="final-report markdown-report">
          {data.final_report ? (
            <MarkdownContent>{data.final_report}</MarkdownContent>
          ) : (
            <p className="empty-result">No final report was returned.</p>
          )}
        </div>
      </section>

      <section className="results-section">
        <SectionHeading
          icon="◈"
          title="Best sources"
          description="Sources selected by the source intelligence system."
          count={sources.length}
        />
        <div className="best-sources-list">
          {sources.length ? sources.map((source, index) => (
            <article
              className="source-card"
              key={`${source.url || source.title || "source"}-${index}`}
            >
              <div className="source-rank">
                {String(source.rank || index + 1).padStart(2, "0")}
              </div>
              <div className="source-content">
                <h4>
                  {source.url ? (
                    <a href={source.url} target="_blank" rel="noopener noreferrer">
                      {source.title || "Untitled source"} ↗
                    </a>
                  ) : source.title || "Untitled source"}
                </h4>
                <span className="source-domain">
                  {source.domain || source.url || "Unknown domain"}
                </span>
                <p>
                  {source.snippet || source.text?.slice(0, 360) ||
                    "No source description available."}
                </p>
                <div className="source-meta">
                  <span>
                    Relevance score:{" "}
                    {source.overall_score != null
                      ? Number(source.overall_score).toFixed(1)
                      : "—"}
                  </span>
                  <span>{source.recommendation || "Evaluated source"}</span>
                </div>
              </div>
            </article>
          )) : <p className="empty-result">No sources were returned.</p>}
        </div>
      </section>

      <section className="results-section">
        <SectionHeading
          icon="✓"
          title="Evidence intelligence"
          description="Evidence coverage reflects relevance to source passages; it does not independently verify factual correctness."
        />
        <div className="evidence-summary">
          <div><span>Evidence coverage</span><strong>{coverage != null ? `${coverage}%` : "—"}</strong></div>
          <div><span>Strong evidence</span><strong>{evidenceSummary.strong ?? 0}</strong></div>
          <div><span>Weak evidence</span><strong>{evidenceSummary.weak ?? 0}</strong></div>
          <div><span>Unsupported claims</span><strong>{evidenceSummary.unsupported_claims ?? 0}</strong></div>
        </div>
      </section>

      <section className="results-section">
        <SectionHeading
          icon="⚖"
          title="Contradiction analysis"
          description="Relationships and uncertainties detected across sources."
        />
        <div className="contradiction-panel">
          <div className="contradiction-status">
            <strong>
              {contradictionSummary.overall_status || "No summary available"}
            </strong>
            <span>
              {contradictionSummary.contradictions ?? 0} contradictions ·{" "}
              {contradictionSummary.uncertainties ?? 0} uncertainties ·{" "}
              {contradictionSummary.agreements ?? 0} agreements
            </span>
          </div>
        </div>
      </section>

      <section className="results-section">
        <SectionHeading
          icon="✓"
          title="Fact checking"
          description="Assessments against the collected source material."
        />
        <div className="analysis-card markdown-report">
          {factChecking ? <MarkdownContent>{factChecking}</MarkdownContent> :
            <p className="empty-result">No fact-checking details returned.</p>}
        </div>
      </section>

      <section className="results-section">
        <SectionHeading
          icon="◉"
          title="Research analysis"
          description="Cross-source themes, differences, and insights."
        />
        <div className="analysis-card markdown-report">
          {analysis ? <MarkdownContent>{analysis}</MarkdownContent> :
            <p className="empty-result">No analysis details returned.</p>}
        </div>
      </section>

      <footer className="results-footer">
        ✦ Research complete. Verify important claims against original sources.
      </footer>
    </section>
  );
}
