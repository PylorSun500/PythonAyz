from __future__ import annotations

from pathlib import Path

import storage
from app import app


def main() -> None:
    temp_file = Path(__file__).resolve().parent / "_smoke_test_bills.xlsx"
    if temp_file.exists():
        temp_file.unlink()

    storage.DATA_FILE = temp_file

    client = app.test_client()

    dashboard_response = client.get("/api/dashboard")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.get_json()
    assert dashboard["settings"]["daily_budget"] == 120.0
    assert temp_file.exists()

    settings_response = client.post(
        "/api/settings",
        json={"daily_budget": 100, "weekly_budget": 500},
    )
    assert settings_response.status_code == 200
    settings_payload = settings_response.get_json()
    assert settings_payload["dashboard"]["settings"]["daily_budget"] == 100.0
    assert settings_payload["dashboard"]["settings"]["weekly_budget"] == 500.0

    first_bill_response = client.post(
        "/api/bills",
        json={
            "date": dashboard["stats"]["today"],
            "category": "餐饮",
            "amount": 80,
            "note": "午饭",
        },
    )
    assert first_bill_response.status_code == 200
    first_payload = first_bill_response.get_json()
    assert first_payload["dashboard"]["stats"]["today_total"] == 80.0
    assert first_payload["dashboard"]["stats"]["week_penalty_applied"] == 0.0

    overspend_response = client.post(
        "/api/bills",
        json={
            "date": dashboard["stats"]["today"],
            "category": "购物",
            "amount": 50,
            "note": "文具",
        },
    )
    assert overspend_response.status_code == 409
    overspend_payload = overspend_response.get_json()
    assert overspend_payload["review"]["requires_reason"] is True
    assert overspend_payload["review"]["overage_amount"] == 30.0

    confirm_response = client.post(
        "/api/bills",
        json={
            "date": dashboard["stats"]["today"],
            "category": "购物",
            "amount": 50,
            "note": "文具",
            "overspend_reason": "课程展示急需购买材料",
        },
    )
    assert confirm_response.status_code == 200
    confirm_payload = confirm_response.get_json()
    assert confirm_payload["dashboard"]["stats"]["today_total"] == 130.0
    assert confirm_payload["dashboard"]["stats"]["today_overage"] == 30.0
    assert confirm_payload["dashboard"]["stats"]["week_penalty_applied"] == 30.0
    assert confirm_payload["dashboard"]["stats"]["week_remaining"] == 340.0
    assert len(confirm_payload["dashboard"]["bills"]) == 2
    assert len(confirm_payload["dashboard"]["category_breakdown"]) == 2

    temp_file.unlink(missing_ok=True)
    print("smoke-test-ok")


if __name__ == "__main__":
    main()
