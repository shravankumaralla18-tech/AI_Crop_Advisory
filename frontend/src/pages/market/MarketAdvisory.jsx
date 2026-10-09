import { useEffect, useState } from "react";
import Alert from "../../components/Alert.jsx";
import CropCard from "../../components/CropCard.jsx";
import Loading from "../../components/Loading.jsx";
import MarketCard from "../../components/MarketCard.jsx";
import { listCrops } from "../../services/advisoryService";
import { getMarketAdvisory } from "../../services/marketService";
import { errorMessage } from "../../utils/helpers";

export default function MarketAdvisory() {
  const [crops, setCrops] = useState([]);
  const [selected, setSelected] = useState(null);
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listCrops().then(setCrops).catch((e) => setError(errorMessage(e)));
  }, []);

  async function choose(id) {
    setSelected(id);
    setLoading(true);
    setError("");
    try {
      setAdvisory(await getMarketAdvisory(id));
    } catch (e) {
      setError(errorMessage(e));
      setAdvisory(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>Sell or hold?</h1>
        <p>Pick a crop to compare its latest available record with recent trends and markets.</p>
      </div>
      <Alert>{error}</Alert>
      <div className="grid" style={{ marginBottom: "1.5rem" }}>
        {crops.map((c) => <CropCard key={c.id} crop={c} selected={selected === c.id} onSelect={choose} />)}
      </div>
      {loading && <Loading />}
      {advisory && !loading && <MarketCard advisory={advisory} />}
    </>
  );
}
