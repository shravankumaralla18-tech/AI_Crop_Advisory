import { SIGNAL_LABELS } from "../utils/constants";
import { formatPrice } from "../utils/helpers";

export default function MarketCard({ advisory }) {
  return (
    <article className="card">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h3 style={{ margin: 0 }}>{advisory.crop_name}</h3>
        <span className={`tag ${advisory.signal}`}>{SIGNAL_LABELS[advisory.signal]}</span>
      </div>
      <h2 style={{ marginTop: ".6rem" }}>{advisory.headline}</h2>
      <p>{advisory.reason}</p>
      <p className="muted">
        Latest ({advisory.data_date}) {formatPrice(advisory.latest_price, advisory.currency)} per {advisory.unit}. 30-day average{" "}
        {formatPrice(advisory.avg_30d, advisory.currency)}.
      </p>
      <p>
        Highest available quote: <strong>{advisory.best_market}</strong> at {formatPrice(advisory.best_market_price, advisory.currency)}.
      </p>
      {advisory.is_sample && <p className="market-sample-note">Sample data only, not live market prices. Source: {advisory.source}</p>}
      <p className="muted" style={{ fontSize: ".9rem", marginBottom: 0 }}>{advisory.disclaimer}</p>
    </article>
  );
}
