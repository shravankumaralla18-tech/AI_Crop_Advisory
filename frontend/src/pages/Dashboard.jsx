import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Alert from "../components/Alert.jsx";
import DiseaseCard from "../components/DiseaseCard.jsx";
import Loading from "../components/Loading.jsx";
import PriceChart from "../components/PriceChart.jsx";
import useAuth from "../hooks/useAuth";
import * as diseaseService from "../services/diseaseService";
import { getRecommendations, listCrops } from "../services/advisoryService";
import { getPrices, getTrends } from "../services/marketService";
import { SIGNAL_LABELS } from "../utils/constants";
import { errorMessage, formatPrice } from "../utils/helpers";

export default function Dashboard() {
  const { user } = useAuth();
  const [crops, setCrops] = useState([]);
  const [history, setHistory] = useState([]);
  const [recs, setRecs] = useState([]);
  const [marketRows, setMarketRows] = useState([]);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    let active = true;
    async function loadDashboard() {
      const failures = [];
      const [cropResult, historyResult, recResult, priceResult] = await Promise.allSettled([
        listCrops(),
        diseaseService.getHistory(),
        getRecommendations(),
        getPrices(),
      ]);
      if (!active) return;

      if (cropResult.status === "fulfilled") setCrops(cropResult.value);
      else failures.push(errorMessage(cropResult.reason, "Could not load supported crops."));
      if (historyResult.status === "fulfilled") setHistory(historyResult.value.slice(0, 3));
      else failures.push(errorMessage(historyResult.reason, "Could not load recent leaf checks."));
      if (recResult.status === "fulfilled") setRecs(recResult.value);
      else failures.push(errorMessage(recResult.reason, "Could not load seasonal advice."));
      if (priceResult.status === "fulfilled") {
        setMarketRows(priceResult.value);
        const firstCrop = priceResult.value[0]?.crop_id;
        if (firstCrop) {
          try {
            const points = await getTrends(firstCrop, 30);
            if (active) setTrend(points);
          } catch (err) {
            failures.push(errorMessage(err, "Could not load sample price trends."));
          }
        }
      } else failures.push(errorMessage(priceResult.reason, "Could not load sample market prices."));

      if (active) {
        setErrors([...new Set(failures)]);
        setLoading(false);
      }
    }
    loadDashboard();
    return () => { active = false; };
  }, []);

  const latestDate = marketRows.reduce((latest, row) => row.date > latest ? row.date : latest, "");
  const latestQuote = marketRows.find((row) => row.date === latestDate);
  const marketCount = new Set(marketRows.map((row) => row.market)).size;

  return (
    <div className="dashboard-page">
      <header className="dashboard-welcome">
        <div>
          <span className="dashboard-eyebrow">FIELD OVERVIEW</span>
          <h1>Good day, {user?.name?.split(" ")[0]}</h1>
          <p>Your crop health and market picture, all in one place.</p>
        </div>
        <div className="row dashboard-actions">
          <Link className="btn" to="/disease">Check a leaf <span aria-hidden="true">&rarr;</span></Link>
          <Link className="btn ghost" to="/market/prices">Check prices</Link>
        </div>
      </header>
      {errors.map((message) => <Alert key={message}>{message}</Alert>)}
      {loading ? (
        <Loading />
      ) : (
        <div className="dashboard-content">
          <section className="dashboard-metrics" aria-label="At a glance">
            <article className="dashboard-metric"><span>SUPPORTED CROPS</span><strong>{crops.length}</strong><small className="dashboard-crop-names">{crops.map((crop) => crop.name).join(", ") || "Crop list unavailable"}</small><Link to="/advisory">Browse crop advice</Link></article>
            <article className="dashboard-metric"><span>RECENT LEAF CHECKS</span><strong>{history.length}</strong><Link to="/disease/history">View history</Link></article>
            <article className="dashboard-metric"><span>SEASONAL ACTIONS</span><strong>{recs.length}</strong><Link to="/advisory/recommendations">See recommendations</Link></article>
            <article className="dashboard-metric"><span>MARKETS IN SAMPLE</span><strong>{marketCount}</strong><Link to="/market/prices">Compare prices</Link></article>
          </section>

          <section className="dashboard-feature-grid">
            <div className="dashboard-section dashboard-market">
              <div className="dashboard-section-head">
                <div><span className="dashboard-eyebrow">MARKET SNAPSHOT</span><h2>Recent sample prices</h2></div>
                <Link to="/market/prices">All prices <span aria-hidden="true">&rarr;</span></Link>
              </div>
              <p className="dashboard-data-note">Development sample data, not live mandi prices.</p>
              {latestQuote ? (
                <>
                  <div className="dashboard-quote">
                    <div><span>{latestQuote.crop_name}</span><strong>{formatPrice(latestQuote.modal_price)}</strong><small>per quintal · {latestQuote.market}, {latestQuote.region}</small></div>
                    <time dateTime={latestQuote.date}>{latestQuote.date}</time>
                  </div>
                  {trend.length > 0 && <PriceChart data={trend} />}
                </>
              ) : <p className="dashboard-empty">Price data is currently unavailable.</p>}
            </div>
            <div className="dashboard-section dashboard-recommendations">
              <div className="dashboard-section-head">
                <div><span className="dashboard-eyebrow">SEASONAL GUIDANCE</span><h2>This month</h2></div>
                <Link to="/advisory/recommendations">View all <span aria-hidden="true">&rarr;</span></Link>
              </div>
              {recs.length === 0 ? (
                <p className="dashboard-empty">No sowing or harvest windows are listed for this month.</p>
              ) : (
                <div className="dashboard-rec-list">
                  {recs.slice(0, 4).map((r) => (
                    <article className="dashboard-rec" key={r.crop_id}>
                      <div><h3>{r.crop_name}</h3><p title={r.reason}>{r.action}. {r.reason}</p></div>
                      <span className={`tag ${r.market_signal}`}>{SIGNAL_LABELS[r.market_signal]}</span>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </section>

          <section className="dashboard-section dashboard-history">
            <div className="dashboard-section-head">
              <div><span className="dashboard-eyebrow">CROP HEALTH</span><h2>Recent leaf checks</h2></div>
              <Link to="/disease/history">View history <span aria-hidden="true">&rarr;</span></Link>
            </div>
            {history.length === 0 ? (
              <div className="dashboard-empty-state"><p>No checks yet. Your first leaf assessment will appear here.</p><Link className="btn small" to="/disease">Upload a leaf photo</Link></div>
            ) : (
              <div className="grid">{history.map((item) => <DiseaseCard key={item.id} result={item} />)}</div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
