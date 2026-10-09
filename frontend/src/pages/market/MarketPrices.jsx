import { useEffect, useState } from "react";
import Alert from "../../components/Alert.jsx";
import Loading from "../../components/Loading.jsx";
import { listCrops } from "../../services/advisoryService";
import { getPrices } from "../../services/marketService";
import { errorMessage, formatPrice } from "../../utils/helpers";

export default function MarketPrices() {
  const [crops, setCrops] = useState([]);
  const [crop, setCrop] = useState("");
  const [region, setRegion] = useState("");
  const [market, setMarket] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [markets, setMarkets] = useState([]);
  const [regions, setRegions] = useState([]);
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { listCrops().then(setCrops).catch(() => {}); }, []);
  useEffect(() => {
    if (startDate && endDate && startDate > endDate) {
      setRows([]);
      setError("Start date must be on or before end date.");
      return;
    }
    setRows(null);
    setError("");
    getPrices({
      crop: crop || undefined,
      region: region || undefined,
      market: market || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    })
      .then((data) => {
        setRows(data);
        setMarkets((current) => current.length ? current : [...new Set(data.map((row) => row.market))].sort());
        setRegions((current) => current.length ? current : [...new Set(data.map((row) => row.region))].sort());
      })
      .catch((e) => { setError(errorMessage(e)); setRows([]); });
  }, [crop, region, market, startDate, endDate]);

  const source = rows?.find((row) => row.is_sample);

  return (
    <>
      <div className="page-head">
        <h1>Prices</h1>
        <p>Latest available price per quintal in each market for the selected filters.</p>
      </div>
      <Alert>{error}</Alert>
      {source?.is_sample && <Alert type="warn">Sample data only, not live mandi prices. Source: {source.source}</Alert>}
      <div className="row market-filters">
        <div>
          <label htmlFor="crop">Crop</label>
          <select id="crop" value={crop} onChange={(e) => setCrop(e.target.value)}>
            <option value="">All crops</option>
            {crops.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="region">Region</label>
          <select id="region" value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">All regions</option>
            {regions.map((r) => <option key={r}>{r}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="market">Market</label>
          <select id="market" value={market} onChange={(e) => setMarket(e.target.value)}>
            <option value="">All markets</option>
            {markets.map((name) => <option key={name}>{name}</option>)}
          </select>
        </div>
        <div><label htmlFor="start-date">From</label><input id="start-date" type="date" value={startDate} max={endDate || undefined} onChange={(e) => setStartDate(e.target.value)} /></div>
        <div><label htmlFor="end-date">To</label><input id="end-date" type="date" value={endDate} min={startDate || undefined} onChange={(e) => setEndDate(e.target.value)} /></div>
      </div>
      {!rows ? <Loading /> : (
        rows.length === 0 ? <p className="muted market-empty">No prices match those filters in the available data.</p> : <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Crop</th><th>Market</th><th>Region</th><th>Date</th><th className="num">Low</th><th className="num">Modal</th><th className="num">High</th><th className="num">7-day change</th></tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={`${r.crop_id}-${r.market}`}>
                  <td>{r.crop_name}</td><td>{r.market}</td><td>{r.region}</td><td>{r.date}</td>
                  <td className="num">{formatPrice(r.min_price)}</td>
                  <td className="num"><strong>{formatPrice(r.modal_price)}</strong></td>
                  <td className="num">{formatPrice(r.max_price)}</td>
                  <td className={`num ${r.change_7d_pct > 0 ? "up" : r.change_7d_pct < 0 ? "down" : ""}`}>
                    {r.change_7d_pct == null ? "-" : `${r.change_7d_pct > 0 ? "+" : ""}${r.change_7d_pct}%`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
