import { useEffect, useState } from "react";
import Alert from "../../components/Alert.jsx";
import Loading from "../../components/Loading.jsx";
import PriceChart from "../../components/PriceChart.jsx";
import { listCrops } from "../../services/advisoryService";
import { getPrices, getTrends } from "../../services/marketService";
import { errorMessage, formatPrice } from "../../utils/helpers";

export default function MarketTrends() {
  const [crops, setCrops] = useState([]);
  const [crop, setCrop] = useState("tomato");
  const [days, setDays] = useState(30);
  const [market, setMarket] = useState("");
  const [markets, setMarkets] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([listCrops(), getPrices()])
      .then(([cropRows, priceRows]) => {
        setCrops(cropRows);
        setMarkets([...new Set(priceRows.map((row) => row.market))].sort());
      })
      .catch((e) => setError(errorMessage(e)));
  }, []);
  useEffect(() => {
    if (startDate && endDate && startDate > endDate) {
      setData([]);
      setError("Start date must be on or before end date.");
      return;
    }
    setData(null);
    setError("");
    getTrends(crop, startDate || endDate ? 90 : days, {
      market: market || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    }).then(setData).catch((e) => { setError(errorMessage(e)); setData([]); });
  }, [crop, days, market, startDate, endDate]);

  const first = data?.[0]?.price;
  const last = data?.[data.length - 1]?.price;
  const change = first && last ? ((last - first) / first) * 100 : null;

  return (
    <>
      <div className="page-head">
        <h1>Price trends</h1>
        <p>Historical modal price by date. Choose a market or date range to narrow the view.</p>
      </div>
      <Alert>{error}</Alert>
      {data?.[0]?.is_sample && <Alert type="warn">Sample data only, not live mandi prices. Source: {data[0].source}</Alert>}
      <div className="row market-filters">
        <div>
          <label htmlFor="crop">Crop</label>
          <select id="crop" value={crop} onChange={(e) => setCrop(e.target.value)}>
            {crops.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="days">Period</label>
          <select id="days" value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={45}>Last 45 days</option>
          </select>
        </div>
        <div>
          <label htmlFor="trend-market">Market</label>
          <select id="trend-market" value={market} onChange={(e) => setMarket(e.target.value)}>
            <option value="">All markets</option>
            {markets.map((name) => <option key={name}>{name}</option>)}
          </select>
        </div>
        <div><label htmlFor="trend-start">From</label><input id="trend-start" type="date" value={startDate} max={endDate || undefined} onChange={(e) => setStartDate(e.target.value)} /></div>
        <div><label htmlFor="trend-end">To</label><input id="trend-end" type="date" value={endDate} min={startDate || undefined} onChange={(e) => setEndDate(e.target.value)} /></div>
      </div>
      {!data && !error ? <Loading /> : data?.length > 0 ? (
        <div className="card">
          <p>
            Now <strong>{formatPrice(last)}</strong> per quintal.{" "}
            <span className={change >= 0 ? "up" : "down"}>{change >= 0 ? "Up" : "Down"} {Math.abs(change).toFixed(1)}%</span> over {days} days.
          </p>
          <PriceChart data={data} />
        </div>
      ) : !error && <p className="muted market-empty">No trend data is available for those filters.</p>}
    </>
  );
}
