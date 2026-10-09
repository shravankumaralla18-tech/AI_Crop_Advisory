from datetime import date

import pytest
from fastapi import HTTPException

from app.services import advisory_service, market_service


def test_prices_cover_all_markets_for_crop():
    rows = market_service.get_prices("tomato")
    assert len(rows) == 4
    assert all(r["crop_id"] == "tomato" for r in rows)


def test_prices_filter_market_and_date_and_label_sample_source():
    rows = market_service.get_prices(
        "tomato", market="Market A", start_date=date(2026, 10, 7), end_date=date(2026, 10, 7)
    )
    assert len(rows) == 1
    assert rows[0]["market"] == "Market A"
    assert rows[0]["date"] == "2026-10-07"
    assert rows[0]["is_sample"] is True
    assert "Synthetic sample data" in rows[0]["source"]


def test_reverse_date_range_is_rejected():
    with pytest.raises(HTTPException) as e:
        market_service.get_prices("tomato", start_date=date(2026, 10, 7), end_date=date(2026, 10, 6))
    assert e.value.status_code == 422


def test_trends_length_and_order():
    series = market_service.get_trends("potato", 30)
    assert len(series) == 30
    assert [p["date"] for p in series] == sorted(p["date"] for p in series)


def test_trends_can_filter_to_market_and_date_range():
    series = market_service.get_trends(
        "potato", 90, market="Market B", start_date=date(2026, 10, 1), end_date=date(2026, 10, 3)
    )
    assert [point["date"] for point in series] == ["2026-10-01", "2026-10-02", "2026-10-03"]
    assert all(point["is_sample"] for point in series)


def test_advisory_has_valid_signal():
    adv = market_service.get_advisory("wheat")
    assert adv["signal"] in {"sell", "hold", "monitor"}
    assert adv["reason"]


def test_unknown_crop_is_404():
    with pytest.raises(HTTPException) as e:
        market_service.get_trends("banana")
    assert e.value.status_code == 404


def test_recommendations_for_october_include_wheat():
    ids = {r["crop_id"] for r in advisory_service.get_recommendations(10)}
    assert "wheat" in ids
