from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from analytics import week_start_for


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "bills_data.xlsx"

BILLS_COLUMNS = [
    "id",
    "date",
    "category",
    "amount",
    "note",
    "overspend_reason",
    "penalty_applied",
    "created_at",
]

SETTINGS_KEYS = [
    "daily_budget",
    "weekly_budget",
    "weekly_penalty_used",
    "active_week_start",
]


def _default_settings() -> dict[str, float | str]:
    return {
        "daily_budget": 120.0,
        "weekly_budget": 800.0,
        "weekly_penalty_used": 0.0,
        "active_week_start": week_start_for(date.today()).isoformat(),
    }


def _settings_to_frame(settings: dict[str, float | str]) -> pd.DataFrame:
    normalized = {key: settings[key] for key in SETTINGS_KEYS}
    return pd.DataFrame({"key": list(normalized.keys()), "value": list(normalized.values())})


def _normalize_bills_frame(bills_df: pd.DataFrame | None = None) -> pd.DataFrame:
    frame = bills_df.copy() if bills_df is not None else pd.DataFrame(columns=BILLS_COLUMNS)
    for column in BILLS_COLUMNS:
        if column not in frame.columns:
            frame[column] = "" if column not in {"amount", "penalty_applied"} else 0.0

    frame = frame[BILLS_COLUMNS]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame["date"] = frame["date"].fillna("")
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0.0)
    frame["penalty_applied"] = pd.to_numeric(frame["penalty_applied"], errors="coerce").fillna(0.0)
    text_columns = ["id", "category", "note", "overspend_reason", "created_at"]
    for column in text_columns:
        frame[column] = frame[column].fillna("").astype(str)
    return frame


def _normalize_settings_frame(settings_df: pd.DataFrame | None = None) -> pd.DataFrame:
    defaults = _default_settings()
    if settings_df is None or settings_df.empty or "key" not in settings_df.columns or "value" not in settings_df.columns:
        return _settings_to_frame(defaults)

    mapped = defaults.copy()
    raw_map = dict(zip(settings_df["key"].astype(str), settings_df["value"]))
    for key in SETTINGS_KEYS:
        if key in raw_map:
            mapped[key] = raw_map[key]
    return _settings_to_frame(mapped)


def _settings_frame_to_dict(settings_df: pd.DataFrame) -> dict[str, float | str]:
    mapping = dict(zip(settings_df["key"].astype(str), settings_df["value"]))
    return {
        "daily_budget": float(mapping["daily_budget"]),
        "weekly_budget": float(mapping["weekly_budget"]),
        "weekly_penalty_used": float(mapping["weekly_penalty_used"]),
        "active_week_start": str(mapping["active_week_start"]),
    }


def _write_workbook(bills_df: pd.DataFrame, settings: dict[str, float | str]) -> None:
    with pd.ExcelWriter(DATA_FILE, engine="openpyxl") as writer:
        _normalize_bills_frame(bills_df).to_excel(writer, sheet_name="bills", index=False)
        _settings_to_frame(settings).to_excel(writer, sheet_name="settings", index=False)


def ensure_workbook() -> None:
    if DATA_FILE.exists():
        return
    _write_workbook(pd.DataFrame(columns=BILLS_COLUMNS), _default_settings())


def load_workbook_state() -> tuple[pd.DataFrame, dict[str, float | str]]:
    ensure_workbook()

    try:
        bills_df = pd.read_excel(DATA_FILE, sheet_name="bills")
    except ValueError:
        bills_df = pd.DataFrame(columns=BILLS_COLUMNS)

    try:
        settings_df = pd.read_excel(DATA_FILE, sheet_name="settings")
    except ValueError:
        settings_df = _settings_to_frame(_default_settings())

    bills_df = _normalize_bills_frame(bills_df)
    settings = _settings_frame_to_dict(_normalize_settings_frame(settings_df))

    current_week = week_start_for(date.today()).isoformat()
    if settings["active_week_start"] != current_week:
        settings["active_week_start"] = current_week
        settings["weekly_penalty_used"] = 0.0
        _write_workbook(bills_df, settings)

    return bills_df, settings


def update_budget_settings(daily_budget: float, weekly_budget: float) -> tuple[pd.DataFrame, dict[str, float | str]]:
    bills_df, settings = load_workbook_state()
    settings["daily_budget"] = round(float(daily_budget), 2)
    settings["weekly_budget"] = round(float(weekly_budget), 2)
    _write_workbook(bills_df, settings)
    return bills_df, settings


def add_bill_record(record: dict) -> tuple[pd.DataFrame, dict[str, float | str]]:
    bills_df, settings = load_workbook_state()
    next_row = pd.DataFrame([record], columns=BILLS_COLUMNS)
    bills_df = pd.concat([bills_df, next_row], ignore_index=True)
    settings["weekly_penalty_used"] = round(
        float(settings["weekly_penalty_used"]) + float(record.get("penalty_applied", 0.0)),
        2,
    )
    _write_workbook(bills_df, settings)
    return _normalize_bills_frame(bills_df), settings
