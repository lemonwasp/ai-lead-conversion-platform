type HistoricalPredictedLabel = 0 | 1 | 2;

type LeadSummary = {
  leadId: string;
  name: string;
  source: string;
  salesUnit: string;
  priority: string;
  predictedLabel: HistoricalPredictedLabel;
};

const reconstructionLead: LeadSummary = {
  leadId: "SYN-2024-001",
  name: "Northstar Manufacturing",
  source: "Industry event",
  salesUnit: "Central Europe",
  priority: "High",
  predictedLabel: 2,
};

const reconstructionDraft =
  `Hello ${reconstructionLead.name},\n\n` +
  `I'm reaching out from our ${reconstructionLead.salesUnit} sales team regarding a lead ` +
  `recorded through ${reconstructionLead.source}. If a conversation would be useful, we'd be ` +
  "happy to arrange a follow-up at a convenient time.\n\n" +
  "Best regards,\nSales team";

const predictionCopy: Record<
  HistoricalPredictedLabel,
  { title: string; description: string }
> = {
  0: {
    title: "Other",
    description: "No historical qualified or converted outcome is represented.",
  },
  1: {
    title: "Converted",
    description: "Historical target class for a converted lead outcome.",
  },
  2: {
    title: "Qualified",
    description: "Historical target class for a qualified lead outcome.",
  },
};

/** Render the privacy-safe historical lead, prediction, and outreach fixture. */
export function App() {
  const prediction = predictionCopy[reconstructionLead.predictedLabel];

  return (
    <main className="page-shell">
      <section className="dashboard" aria-labelledby="dashboard-title">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">2024 reconstruction</p>
            <h1 id="dashboard-title">Lead conversion review</h1>
            <p className="intro">
              Privacy-safe preview of the lead, prediction, and outreach review flow.
            </p>
          </div>
          <span className="fixture-label">Synthetic fixture</span>
        </header>

        <article className="lead-card">
          <div className="lead-heading">
            <div>
              <p className="section-label">Lead</p>
              <h2>{reconstructionLead.name}</h2>
              <p className="lead-id">{reconstructionLead.leadId}</p>
            </div>

            <div
              className="prediction-badge"
              aria-label={`Predicted label ${reconstructionLead.predictedLabel}: ${prediction.title}`}
            >
              <span>Predicted label</span>
              <strong>{reconstructionLead.predictedLabel}</strong>
              <small>{prediction.title}</small>
            </div>
          </div>

          <dl className="lead-details">
            <div>
              <dt>Source</dt>
              <dd>{reconstructionLead.source}</dd>
            </div>
            <div>
              <dt>Sales unit</dt>
              <dd>{reconstructionLead.salesUnit}</dd>
            </div>
            <div>
              <dt>Priority</dt>
              <dd>{reconstructionLead.priority}</dd>
            </div>
          </dl>

          <footer className="prediction-note">
            <span>Historical class meaning</span>
            <p>{prediction.description}</p>
          </footer>
        </article>

        <article className="outreach-card" aria-labelledby="outreach-title">
          <div className="outreach-heading">
            <div>
              <p className="section-label">Outreach draft</p>
              <h2 id="outreach-title">Customer message review</h2>
            </div>
            <span className="review-label">Human review required</span>
          </div>

          <div className="draft-copy" aria-label="Synthetic outreach draft">
            {reconstructionDraft.split("\n").map((line, index) =>
              line ? <p key={index}>{line}</p> : <br key={index} />,
            )}
          </div>

          <footer className="outreach-note">
            Synthetic reconstruction fixture only. This panel is not yet connected to
            the outreach draft API.
          </footer>
        </article>
      </section>
    </main>
  );
}
