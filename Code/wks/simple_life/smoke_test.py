from __future__ import annotations

from io import BytesIO

from app import app, build_budget_plan, write_excel_report


def main() -> None:
    plan = build_budget_plan(6000, 0.10)
    assert round(plan["monthly_salary"], 2) == 6000.00
    assert round(plan["savings_amount"], 2) == 600.00
    assert len(plan["items"]) == 5
    assert round(sum(item["amount"] for item in plan["items"]) + plan["savings_amount"], 2) == 6000.00

    output = BytesIO()
    write_excel_report(plan, output)
    assert output.getbuffer().nbytes > 0

    client = app.test_client()
    budget_response = client.post("/api/budget", json={"salary": 6000, "savings_ratio": 10})
    assert budget_response.status_code == 200
    payload = budget_response.get_json()
    assert payload["plan"]["items"][0]["category"] == "房租"

    export_response = client.post("/api/export", json={"salary": 6000, "savings_ratio": 10})
    assert export_response.status_code == 200
    assert export_response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    print("smoke-test-ok")


if __name__ == "__main__":
    main()
