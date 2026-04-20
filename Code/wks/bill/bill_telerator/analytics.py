from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd


def week_start_for(target: date) -> date:
    return target - timedelta(days=target.weekday())


def _to_date_array(bills_df: pd.DataFrame) -> np.ndarray:
    if bills_df.empty:
        return np.array([], dtype="datetime64[D]")
    return pd.to_datetime(bills_df["date"], errors="coerce").to_numpy(dtype="datetime64[D]")


def _to_amount_array(bills_df: pd.DataFrame) -> np.ndarray:
    if bills_df.empty:
        return np.array([], dtype=float)
    return pd.to_numeric(bills_df["amount"], errors="coerce").fillna(0.0).to_numpy(dtype=float)


def _to_category_array(bills_df: pd.DataFrame) -> np.ndarray:
    if bills_df.empty:
        return np.array([], dtype=str)
    return bills_df["category"].fillna("未分类").astype(str).to_numpy(dtype=str)


def evaluate_bill_submission(
    bills_df: pd.DataFrame,
    settings: dict[str, float | str],
    category: str,
    amount: float,
    note: str,
    bill_date: str,
) -> dict:
    parsed_bill_date = pd.to_datetime(bill_date, errors="coerce")
    if pd.isna(parsed_bill_date):
        raise ValueError("账单日期格式不正确。")

    clean_bill_date = parsed_bill_date.date()
    bill_day = np.datetime64(clean_bill_date)
    dates = _to_date_array(bills_df)
    amounts = _to_amount_array(bills_df)
    daily_budget = float(settings["daily_budget"])

    same_day_mask = dates == bill_day
    today_total_before = float(np.sum(amounts[same_day_mask]))
    today_total_after = today_total_before + float(amount)

    previous_overage = float(np.maximum(today_total_before - daily_budget, 0.0))
    current_overage = float(np.maximum(today_total_after - daily_budget, 0.0))
    penalty_increment = current_overage - previous_overage

    review_columns = ["date", "category", "amount", "note", "overspend_reason", "created_at"]
    review_df = bills_df.loc[same_day_mask, review_columns].copy()
    if not review_df.empty:
        review_df = review_df.sort_values(by="created_at", ascending=False, na_position="last")
        review_df = review_df.drop(columns=["created_at"])

    today_records = review_df.to_dict(orient="records")
    today_records.insert(
        0,
        {
            "date": clean_bill_date.isoformat(),
            "category": category,
            "amount": float(amount),
            "note": note,
            "overspend_reason": "待补充",
            "is_pending": True,
        },
    )

    return {
        "requires_reason": today_total_after > daily_budget,
        "today_total_before": round(today_total_before, 2),
        "today_total_after": round(today_total_after, 2),
        "daily_budget": round(daily_budget, 2),
        "overage_amount": round(current_overage, 2),
        "penalty_increment": round(penalty_increment, 2),
        "bill_date": clean_bill_date.isoformat(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "today_records": today_records,
    }


def build_dashboard_payload(bills_df: pd.DataFrame, settings: dict[str, float | str]) -> dict:
    today = date.today()
    week_start = week_start_for(today)
    week_end = week_start + timedelta(days=6)
    today_day = np.datetime64(today)
    week_start_day = np.datetime64(week_start)
    week_end_day = np.datetime64(week_end)
    dates = _to_date_array(bills_df)
    amounts = _to_amount_array(bills_df)
    categories = _to_category_array(bills_df)

    today_mask = dates == today_day
    week_mask = (dates >= week_start_day) & (dates <= week_end_day)

    today_total = float(np.sum(amounts[today_mask]))
    week_total = float(np.sum(amounts[week_mask]))

    daily_budget = float(settings["daily_budget"])
    weekly_budget = float(settings["weekly_budget"])
    weekly_penalty_used = float(settings["weekly_penalty_used"])

    high_value_mask = amounts > daily_budget
    high_value_bills = bills_df.loc[high_value_mask, ["date", "category", "amount", "note"]].sort_values(
        by=["date", "amount"],
        ascending=[False, False],
    )

    week_amounts = amounts[week_mask]
    week_categories = categories[week_mask]

    if week_amounts.size and float(np.sum(week_amounts)) > 0:
        unique_categories, category_inverse = np.unique(week_categories, return_inverse=True)
        category_totals = np.zeros(unique_categories.size, dtype=float)
        np.add.at(category_totals, category_inverse, week_amounts)
        category_percentages = (category_totals / np.sum(week_amounts)) * 100
        sorted_index = np.argsort(-category_totals)
        category_breakdown = [
            {
                "category": str(unique_categories[idx]),
                "amount": round(float(category_totals[idx]), 2),
                "percentage": round(float(category_percentages[idx]), 2),
            }
            for idx in sorted_index
        ]
    else:
        category_breakdown = []

    sorted_bills = bills_df.sort_values(by=["date", "created_at"], ascending=[False, False]).copy()
    sorted_bills["amount"] = pd.to_numeric(sorted_bills["amount"], errors="coerce").fillna(0.0).round(2)

    return {
        "settings": {
            "daily_budget": round(daily_budget, 2),
            "weekly_budget": round(weekly_budget, 2),
            "weekly_penalty_used": round(weekly_penalty_used, 2),
            "active_week_start": settings["active_week_start"],
        },
        "stats": {
            "today": today.isoformat(),
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "today_total": round(today_total, 2),
            "week_total": round(week_total, 2),
            "today_remaining": round(daily_budget - today_total, 2),
            "week_remaining": round(weekly_budget - week_total - weekly_penalty_used, 2),
            "today_overage": round(float(np.maximum(today_total - daily_budget, 0.0)), 2),
            "week_penalty_applied": round(weekly_penalty_used, 2),
        },
        "category_breakdown": category_breakdown,
        "bills": sorted_bills.to_dict(orient="records"),
        "high_value_bills": high_value_bills.to_dict(orient="records"),
    }
