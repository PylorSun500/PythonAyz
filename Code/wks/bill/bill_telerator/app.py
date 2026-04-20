from __future__ import annotations

from datetime import date
from uuid import uuid4

from flask import Flask, jsonify, render_template, request

from analytics import build_dashboard_payload, evaluate_bill_submission
from storage import add_bill_record, load_workbook_state, update_budget_settings


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/dashboard")
def dashboard():
    bills_df, settings = load_workbook_state()
    return jsonify(build_dashboard_payload(bills_df, settings))


@app.post("/api/settings")
def save_settings():
    payload = request.get_json(silent=True) or {}

    try:
        daily_budget = float(payload.get("daily_budget", 0))
        weekly_budget = float(payload.get("weekly_budget", 0))
    except (TypeError, ValueError):
        return jsonify({"message": "预算必须是数字。"}), 400

    if daily_budget <= 0 or weekly_budget <= 0:
        return jsonify({"message": "日预算和周预算都必须大于 0。"}), 400

    bills_df, settings = update_budget_settings(daily_budget, weekly_budget)
    return jsonify(
        {
            "message": "预算已更新并写入 Excel。",
            "dashboard": build_dashboard_payload(bills_df, settings),
        }
    )


@app.post("/api/bills")
def add_bill():
    payload = request.get_json(silent=True) or {}

    category = str(payload.get("category", "")).strip()
    note = str(payload.get("note", "")).strip()
    overspend_reason = str(payload.get("overspend_reason", "")).strip()
    bill_date = str(payload.get("date", date.today().isoformat())).strip() or date.today().isoformat()

    try:
        amount = float(payload.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"message": "金额必须是数字。"}), 400

    if not category:
        return jsonify({"message": "请填写消费类别。"}), 400

    if amount <= 0:
        return jsonify({"message": "金额必须大于 0。"}), 400

    bills_df, settings = load_workbook_state()
    try:
        submission_review = evaluate_bill_submission(
            bills_df=bills_df,
            settings=settings,
            category=category,
            amount=amount,
            note=note,
            bill_date=bill_date,
        )
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    if submission_review["requires_reason"] and not overspend_reason:
        return (
            jsonify(
                {
                    "message": "今日支出将超出日预算，请先填写超支原因后再保存。",
                    "review": submission_review,
                }
            ),
            409,
        )

    record = {
        "id": str(uuid4()),
        "date": submission_review["bill_date"],
        "category": category,
        "amount": amount,
        "note": note,
        "overspend_reason": overspend_reason,
        "penalty_applied": submission_review["penalty_increment"],
        "created_at": submission_review["created_at"],
    }

    bills_df, settings = add_bill_record(record)
    return jsonify(
        {
            "message": "账单已写入 Excel。",
            "dashboard": build_dashboard_payload(bills_df, settings),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
