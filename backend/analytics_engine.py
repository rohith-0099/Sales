from __future__ import annotations

from datetime import datetime, timedelta
import re
from threading import Lock
from typing import Any
from uuid import uuid4

import pandas as pd
from prophet import Prophet


DATE_COLUMN_CANDIDATES = [
    "date",
    "order_date",
    "orderdate",
    "invoice_date",
    "invoicedate",
    "sales_date",
    "transaction_date",
    "transactiondate",
    "ship_date",
    "shipdate",
    "timestamp",
    "datetime",
    "ds",
]
YEAR_COLUMN_CANDIDATES = ["year", "fiscal_year"]
MONTH_COLUMN_CANDIDATES = ["month", "period_month"]
DAY_COLUMN_CANDIDATES = ["day", "day_of_month"]
DATE_COLUMN_KEYWORDS = ["date", "time", "timestamp", "period"]
YEAR_MONTH_COLUMN_CANDIDATES = ["year_month", "month_year", "period", "monthyear"]
SALES_COLUMN_CANDIDATES = [
    "sales",
    "sale",
    "total_sales",
    "gross_sales",
    "sales_value",
    "sale_value",
    "sales_amount",
    "sales_inr",
    "revenue_inr",
    "revenue",
    "total_revenue",
    "gross_revenue",
    "amount",
    "net_sales",
    "turnover",
    "gmv",
]
SALES_COLUMN_KEYWORDS = ["sales", "sale", "revenue", "turnover", "gmv"]
SALES_COLUMN_HINTS = ["total", "gross", "net", "value", "amount", "inr", "usd", "rs"]
PRODUCT_NAME_COLUMN_CANDIDATES = [
    "product_name",
    "product",
    "item_name",
    "item",
    "name",
    "product_sub_category",
    "product_subcategory",
    "sub_category",
    "subcategory",
    "product_type",
    "product_category",
    "category",
]
PRODUCT_ID_COLUMN_CANDIDATES = [
    "product_id",
    "product_code",
    "item_identifier",
    "sku",
    "item_code",
]
PRODUCT_CONTEXT_COLUMN_CANDIDATES = [
    "product_type",
    "product_category",
    "category",
    "segment",
    "product_container",
]
PRODUCT_LOOKUP_CANDIDATES = (
    PRODUCT_NAME_COLUMN_CANDIDATES
    + PRODUCT_ID_COLUMN_CANDIDATES
    + PRODUCT_CONTEXT_COLUMN_CANDIDATES
)

FREQUENCY_PROFILES = {
    "daily": {
        "prophet_freq": "D",
        "default_periods": 30,
        "history_limit": 180,
        "comparison_window": 7,
        "daily_seasonality": True,
        "weekly_seasonality": True,
        "yearly_seasonality": True,
        "future_label": "days",
    },
    "weekly": {
        "prophet_freq": "W",
        "default_periods": 12,
        "history_limit": 104,
        "comparison_window": 4,
        "daily_seasonality": False,
        "weekly_seasonality": False,
        "yearly_seasonality": True,
        "future_label": "weeks",
    },
    "monthly": {
        "prophet_freq": "MS",
        "default_periods": 12,
        "history_limit": 60,
        "comparison_window": 3,
        "daily_seasonality": False,
        "weekly_seasonality": False,
        "yearly_seasonality": True,
        "future_label": "months",
    },
    "yearly": {
        "prophet_freq": "YS",
        "default_periods": 3,
        "history_limit": 20,
        "comparison_window": 2,
        "daily_seasonality": False,
        "weekly_seasonality": False,
        "yearly_seasonality": False,
        "future_label": "years",
    },
}


def _canonical(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return normalized.strip("_")


def _build_column_map(columns: list[str]) -> dict[str, str]:
    return {_canonical(column): column for column in columns}


def _first_column(column_map: dict[str, str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in column_map:
            return column_map[candidate]
    return None


def _find_sales_column(column_map: dict[str, str]) -> str | None:
    exact_match = _first_column(column_map, SALES_COLUMN_CANDIDATES)
    if exact_match:
        return exact_match

    scored_matches: list[tuple[int, str, str]] = []
    for canonical_name, original_name in column_map.items():
        score = 0
        if any(keyword in canonical_name for keyword in SALES_COLUMN_KEYWORDS):
            score += 5
        if any(hint in canonical_name for hint in SALES_COLUMN_HINTS):
            score += 1

        if score > 0:
            scored_matches.append((score, canonical_name, original_name))

    if not scored_matches:
        return None

    scored_matches.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return scored_matches[0][2]


def _is_likely_datetime_series(series: pd.Series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False

    # Avoid treated plain small integers (like years) as nanosecond-based timestamps (1970)
    if pd.api.types.is_integer_dtype(non_null):
        if non_null.min() > 1000 and non_null.max() < 3000:
            return False

    sample = non_null.head(25)
    parsed = pd.to_datetime(sample, errors="coerce")
    
    # Check if we got something other than the 1970-01-01 epoch for all rows
    if bool(parsed.notna().all()) and bool((parsed.dt.year == 1970).all()):
        return False
        
    return bool(float(parsed.notna().mean()) >= 0.6)


def _find_date_column(df: pd.DataFrame, column_map: dict[str, str]) -> str | None:
    exact_match = _first_column(column_map, DATE_COLUMN_CANDIDATES)
    if exact_match:
        return exact_match

    year_month_match = _first_column(column_map, YEAR_MONTH_COLUMN_CANDIDATES)
    if year_month_match:
        return year_month_match

    scored_matches: list[tuple[int, str, str]] = []
    for canonical_name, original_name in column_map.items():
        score = 0
        if any(keyword in canonical_name for keyword in DATE_COLUMN_KEYWORDS):
            score += 5
        if canonical_name.endswith("dt"):
            score += 2
        if score > 0 and _is_likely_datetime_series(df[original_name]):
            score += 5
        elif score == 0 and _is_likely_datetime_series(df[original_name]):
            score += 4

        if score > 0:
            scored_matches.append((score, canonical_name, original_name))

    if not scored_matches:
        return None

    scored_matches.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return scored_matches[0][2]


def _clean_text(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return text.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})


def _coerce_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = (
        series.astype("string")
        .str.replace(",", "", regex=False)
        .str.replace(r"[^\d\.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _coerce_month(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    month_full = pd.to_datetime(series.astype("string"), format="%B", errors="coerce").dt.month
    month_short = pd.to_datetime(series.astype("string"), format="%b", errors="coerce").dt.month
    return numeric.fillna(month_full).fillna(month_short)


def _build_date_series(df: pd.DataFrame, column_map: dict[str, str]) -> tuple[pd.Series, str | None]:
    direct_date_column = _find_date_column(df, column_map)
    if direct_date_column:
        return pd.to_datetime(df[direct_date_column], errors="coerce"), None

    year_column = _first_column(column_map, YEAR_COLUMN_CANDIDATES)
    month_column = _first_column(column_map, MONTH_COLUMN_CANDIDATES)
    day_column = _first_column(column_map, DAY_COLUMN_CANDIDATES)

    if not year_column:
        available_columns = ", ".join([str(column) for column in df.columns])
        raise ValueError(
            "Could not find a usable date column. Use a date-like column such as `date`, `order date`, "
            "`invoice date`, `ship date`, or provide `year` with optional `month` and `day`. "
            f"Detected columns: {available_columns}"
        )

    years = _coerce_numeric(df[year_column])
    months = _coerce_month(df[month_column]) if month_column else pd.Series(1, index=df.index, dtype="float64")
    days = _coerce_numeric(df[day_column]) if day_column else pd.Series(1, index=df.index, dtype="float64")

    date_parts = pd.DataFrame(
        {
            "year": years,
            "month": months.fillna(1),
            "day": days.fillna(1),
        }
    )
    hint = "yearly" if not month_column else "monthly" if not day_column else "daily"
    return pd.to_datetime(date_parts, errors="coerce"), hint


def infer_granularity(date_series: pd.Series, hint: str | None = None) -> str:
    unique_dates = pd.Series(pd.to_datetime(date_series.dropna().unique())).sort_values()
    if unique_dates.empty:
        return hint or "daily"
    if len(unique_dates) == 1:
        return hint or "daily"

    day_diffs = unique_dates.diff().dropna().dt.days
    median_gap = float(day_diffs.median()) if not day_diffs.empty else 1

    if median_gap >= 330:
        return "yearly"
    if median_gap >= 27:
        return "monthly"
    if median_gap >= 6:
        return "weekly"
    
    # If we have a hint (like 'yearly' from year-only columns) and few points, trust the hint
    if hint and len(unique_dates) < 50:
        return str(hint)

    return str(hint or "daily")


def _build_product_columns(df: pd.DataFrame, column_map: dict[str, str]) -> dict[str, Any]:
    product_name_column = _first_column(column_map, PRODUCT_NAME_COLUMN_CANDIDATES)
    product_id_column = _first_column(column_map, PRODUCT_ID_COLUMN_CANDIDATES)
    product_context_column = _first_column(column_map, PRODUCT_CONTEXT_COLUMN_CANDIDATES)

    lookup_columns: list[str] = []
    for candidate in PRODUCT_LOOKUP_CANDIDATES:
        actual = column_map.get(candidate)
        if actual and actual not in lookup_columns:
            lookup_columns.append(actual)

    if not lookup_columns:
        return {
            "enabled": False,
            "primary_column": None,
            "lookup_columns": [],
            "display_series": pd.Series(pd.NA, index=df.index),
            "search_series": pd.Series("", index=df.index, dtype="string"),
        }

    name_values = _clean_text(df[product_name_column]) if product_name_column else pd.Series(pd.NA, index=df.index)
    id_values = _clean_text(df[product_id_column]) if product_id_column else pd.Series(pd.NA, index=df.index)

    if product_name_column:
        display_values = name_values.copy()
    elif product_id_column:
        display_values = id_values.copy()
    else:
        display_values = _clean_text(df[lookup_columns[0]])

    if product_name_column and product_id_column:
        missing_name = display_values.isna()
        display_values = display_values.where(~missing_name, id_values)

        both_present = display_values.notna() & id_values.notna()
        different_values = both_present & (
            display_values.str.lower() != id_values.str.lower()
        )
        display_values = display_values.where(
            ~different_values,
            display_values + " (" + id_values + ")",
        )

    context_values = (
        _clean_text(df[product_context_column])
        if product_context_column and product_context_column != product_name_column
        else pd.Series(pd.NA, index=df.index)
    )
    add_context = display_values.notna() & context_values.notna()
    different_context = add_context & (
        display_values.str.lower() != context_values.str.lower()
    )
    display_values = display_values.where(
        ~different_context,
        display_values + " (" + context_values + ")",
    )

    search_parts = [_clean_text(df[column]).fillna("") for column in lookup_columns]
    search_frame = pd.concat(search_parts, axis=1) if search_parts else pd.DataFrame(index=df.index)
    search_values = search_frame.apply(
        lambda row: " ".join([value for value in row if value]),
        axis=1,
    ).astype("string").str.lower()

    return {
        "enabled": display_values.notna().any(),
        "primary_column": product_name_column or product_id_column or product_context_column or lookup_columns[0],
        "lookup_columns": lookup_columns,
        "display_series": display_values,
        "search_series": search_values,
    }


def aggregate_sales_series(df: pd.DataFrame) -> pd.DataFrame:
    series_df = (
        df.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )
    return series_df


def _round_or_zero(value: float | int | None) -> float:
    if value is None or pd.isna(value):
        return 0.0
    return round(float(value), 2)


def _safe_growth(current_value: float, previous_value: float) -> float:
    if previous_value == 0:
        return 0.0 if current_value == 0 else 100.0
    return round(((current_value - previous_value) / abs(previous_value)) * 100, 2)


def _serialize_dates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for record in records:
        normalized = {}
        for key, value in record.items():
            if isinstance(value, (pd.Timestamp, datetime)):
                normalized[key] = value.date().isoformat()
            elif pd.isna(value):
                normalized[key] = None
            else:
                normalized[key] = value
        serialized.append(normalized)
    return serialized


def build_upload_stats(df: pd.DataFrame, granularity: str) -> dict[str, Any]:
    series_df = aggregate_sales_series(df)
    profile = FREQUENCY_PROFILES[granularity]

    return {
        "rows": int(len(df)),
        "series_points": int(len(series_df)),
        "total_sales": _round_or_zero(series_df["sales"].sum()),
        "average_sales": _round_or_zero(series_df["sales"].mean()),
        "latest_sales": _round_or_zero(series_df["sales"].iloc[-1] if not series_df.empty else 0),
        "min_sales": _round_or_zero(series_df["sales"].min()),
        "max_sales": _round_or_zero(series_df["sales"].max()),
        "start_date": series_df["date"].min().date().isoformat() if not series_df.empty else None,
        "end_date": series_df["date"].max().date().isoformat() if not series_df.empty else None,
        "granularity": granularity,
        "default_forecast_periods": profile["default_periods"],
    }


def build_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    product_rows = df[df["product_key"].notna()].copy()
    if product_rows.empty:
        return pd.DataFrame(
            columns=["product_key", "total_sales", "average_sales", "record_count", "search_text"]
        )

    grouped = product_rows.groupby("product_key", as_index=False)
    summary = grouped["sales"].agg(total_sales="sum", average_sales="mean", record_count="count")
    search_text = grouped["product_search_text"].agg(
        lambda values: " ".join(pd.Series(values).dropna().astype(str).unique())
    )

    summary["search_text"] = search_text["product_search_text"]
    summary = summary.sort_values(["total_sales", "product_key"], ascending=[False, True]).reset_index(drop=True)
    summary["rank"] = summary.index + 1
    return summary


def prepare_uploaded_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        raise ValueError("The uploaded file is empty.")

    working_df = df.dropna(how="all").copy()
    if working_df.empty:
        raise ValueError("The uploaded file does not contain any usable rows.")

    column_map = _build_column_map(list(working_df.columns))
    sales_column = _find_sales_column(column_map)
    if not sales_column:
        available_columns = ", ".join([str(column) for column in df.columns])
        raise ValueError(
            "Could not find a sales column. Supported names include `sales`, `total sales`, `sales value`, "
            "`revenue`, `turnover`, or `sales_amount`. "
            f"Detected columns: {available_columns}"
        )

    date_series, hint = _build_date_series(working_df, column_map)
    working_df["date"] = date_series
    working_df["sales"] = _coerce_numeric(working_df[sales_column])

    product_meta = _build_product_columns(working_df, column_map)
    if product_meta["enabled"]:
        working_df["product_key"] = product_meta["display_series"]
        working_df["product_search_text"] = product_meta["search_series"]
    else:
        working_df["product_key"] = pd.NA
        working_df["product_search_text"] = pd.Series("", index=working_df.index, dtype="string")

    working_df = (
        working_df.dropna(subset=["date", "sales"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    if working_df.empty:
        raise ValueError("No valid rows remained after parsing dates and sales values.")

    granularity = infer_granularity(working_df["date"], hint)
    product_summary = build_product_summary(working_df)

    preview_columns = ["date", "sales"]
    for column in product_meta["lookup_columns"]:
        if column in working_df.columns and column not in preview_columns:
            preview_columns.append(column)
    if product_meta["enabled"]:
        preview_columns.append("product_key")

    preview = _serialize_dates(working_df[preview_columns].head(10).to_dict("records"))
    stats = build_upload_stats(working_df, granularity)
    stats["unique_products"] = int(len(product_summary))

    return {
        "data": working_df,
        "metadata": {
            "columns": list(df.columns),
            "sales_column": sales_column,
            "granularity": granularity,
            "stats": stats,
            "preview": preview,
            "product_column": "product_key" if product_meta["enabled"] else None,
            "product_primary_column": product_meta["primary_column"],
            "product_lookup_columns": product_meta["lookup_columns"],
            "product_summary": product_summary,
            "sample_products": product_summary.head(8)["product_key"].tolist(),
        },
    }


def filter_dataset_by_product(item: dict[str, Any], selected_product: str | None) -> tuple[pd.DataFrame, str | None]:
    df = item["data"]
    if not selected_product:
        return df.copy(), None

    product_value = selected_product.strip().lower()
    if not product_value:
        return df.copy(), None

    if not item["metadata"]["product_column"]:
        raise ValueError("This upload does not contain product identifiers to filter on.")

    matches = df["product_key"].fillna("").astype(str).str.lower() == product_value
    if not bool(matches.any()):
        raise ValueError(f"Product `{selected_product}` was not found in the uploaded dataset.")

    resolved_product = str(df.loc[matches, "product_key"].iloc[0])
    return df.loc[matches].copy(), resolved_product


def build_period_trends(series_df: pd.DataFrame, granularity: str) -> list[dict[str, Any]]:
    period_df = series_df.copy()

    if granularity in {"daily", "weekly"}:
        period_df["period"] = period_df["date"].dt.to_period("M").dt.to_timestamp()
        period_df["label"] = period_df["period"].dt.strftime("%b %Y")
        grouped = (
            period_df.groupby(["period", "label"], as_index=False)["sales"]
            .agg(total_sales="sum", average_sales="mean")
            .sort_values("period")
            .reset_index(drop=True)
        )
    elif granularity == "monthly":
        period_df["period"] = period_df["date"].dt.to_period("M").dt.to_timestamp()
        period_df["label"] = period_df["period"].dt.strftime("%b %Y")
        grouped = (
            period_df.groupby(["period", "label"], as_index=False)["sales"]
            .agg(total_sales="sum", average_sales="mean")
            .sort_values("period")
            .reset_index(drop=True)
        )
    else:
        period_df["period"] = period_df["date"].dt.to_period("Y").dt.to_timestamp()
        period_df["label"] = period_df["period"].dt.strftime("%Y")
        grouped = (
            period_df.groupby(["period", "label"], as_index=False)["sales"]
            .agg(total_sales="sum", average_sales="mean")
            .sort_values("period")
            .reset_index(drop=True)
        )

    grouped["growth_pct"] = grouped["total_sales"].pct_change().fillna(0).mul(100).round(2)
    return _serialize_dates(grouped.to_dict("records"))


def build_trend_highlights(period_trends: list[dict[str, Any]]) -> dict[str, Any]:
    if not period_trends:
        return {
            "best_period": None,
            "weakest_period": None,
            "momentum": "stable",
        }

    best_period = max(period_trends, key=lambda item: item["total_sales"])
    weakest_period = min(period_trends, key=lambda item: item["total_sales"])
    latest_growth = period_trends[-1].get("growth_pct", 0)

    if latest_growth > 5:
        momentum = "accelerating"
    elif latest_growth < -5:
        momentum = "cooling"
    else:
        momentum = "stable"

    return {
        "best_period": best_period,
        "weakest_period": weakest_period,
        "momentum": momentum,
    }


def build_summary(series_df: pd.DataFrame, granularity: str) -> dict[str, Any]:
    profile = FREQUENCY_PROFILES[granularity]
    comparison_window = min(profile["comparison_window"], max(1, len(series_df) // 2 or 1))

    recent_window = series_df["sales"].tail(comparison_window)
    previous_window = series_df["sales"].iloc[-(comparison_window * 2):-comparison_window]
    if previous_window.empty and len(series_df) > comparison_window:
        previous_window = series_df["sales"].head(comparison_window)

    recent_average = float(recent_window.mean()) if not recent_window.empty else 0.0
    previous_average = float(previous_window.mean()) if not previous_window.empty else 0.0
    growth_pct = _safe_growth(recent_average, previous_average)

    if growth_pct > 5:
        trend_direction = "upward"
    elif growth_pct < -5:
        trend_direction = "downward"
    else:
        trend_direction = "stable"

    volatility_pct = (
        round(float(series_df["sales"].std(ddof=0) / max(series_df["sales"].mean(), 0.01) * 100), 2)
        if len(series_df) > 1
        else 0.0
    )

    return {
        "total_sales": _round_or_zero(series_df["sales"].sum()),
        "average_sales": _round_or_zero(series_df["sales"].mean()),
        "latest_sales": _round_or_zero(series_df["sales"].iloc[-1]),
        "current_run_rate": _round_or_zero(recent_average),
        "previous_run_rate": _round_or_zero(previous_average),
        "growth_pct": growth_pct,
        "trend_direction": trend_direction,
        "volatility_pct": volatility_pct,
        "records": int(len(series_df)),
        "start_date": series_df["date"].min().date().isoformat(),
        "end_date": series_df["date"].max().date().isoformat(),
        "granularity": granularity,
    }


def build_festival_impact(enriched_df: pd.DataFrame, granularity: str) -> dict[str, Any]:
    holiday_sales = enriched_df.groupby("is_holiday")["sales"].mean()
    normal_sales = float(holiday_sales.get(False, 0.0))
    festival_sales = float(holiday_sales.get(True, 0.0))

    impact = {
        "average_sales_normal_days": _round_or_zero(normal_sales),
        "average_sales_festival_days": _round_or_zero(festival_sales),
        "uplift_percentage": _safe_growth(festival_sales, normal_sales) if normal_sales > 0 else 0.0,
        "resolution_note": None,
    }

    if granularity != "daily":
        impact["resolution_note"] = (
            "Festival impact is approximate because the uploaded data is not at day-level granularity."
        )

    return impact


def build_top_festivals(enriched_df: pd.DataFrame) -> list[dict[str, Any]]:
    festival_sales = (
        enriched_df[enriched_df["festival_category"].notna()]
        .groupby("festival_category")["sales"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )

    return [
        {
            "festival": festival,
            "average_sales": _round_or_zero(value),
        }
        for festival, value in festival_sales.items()
    ]


def build_product_leaderboard(product_summary: pd.DataFrame, limit: int = 8) -> list[dict[str, Any]]:
    if product_summary.empty:
        return []

    subset = product_summary.head(limit)
    return [
        {
            "product": row["product_key"],
            "total_sales": _round_or_zero(row["total_sales"]),
            "average_sales": _round_or_zero(row["average_sales"]),
            "records": int(row["record_count"]),
            "rank": int(row["rank"]),
        }
        for _, row in subset.iterrows()
    ]


def build_selected_product_stats(product_summary: pd.DataFrame, selected_product: str | None) -> dict[str, Any] | None:
    if product_summary.empty or not selected_product:
        return None

    match = product_summary[
        product_summary["product_key"].astype(str).str.lower() == selected_product.lower()
    ]
    if match.empty:
        return None

    row = match.iloc[0]
    total_catalog_sales = float(product_summary["total_sales"].sum())
    share_of_sales = (float(row["total_sales"]) / total_catalog_sales * 100) if total_catalog_sales else 0.0

    return {
        "product": row["product_key"],
        "rank": int(row["rank"]),
        "total_sales": _round_or_zero(row["total_sales"]),
        "average_sales": _round_or_zero(row["average_sales"]),
        "records": int(row["record_count"]),
        "share_of_catalog_sales_pct": round(share_of_sales, 2),
    }


def analyze_dataset(item: dict[str, Any], calendar, selected_product: str | None = None) -> dict[str, Any]:
    filtered_df, resolved_product = filter_dataset_by_product(item, selected_product)
    series_df = aggregate_sales_series(filtered_df)

    if series_df.empty:
        raise ValueError("No sales records were available for analysis.")

    enriched_df = calendar.add_festival_features(series_df, "date")
    period_trends = build_period_trends(series_df, item["metadata"]["granularity"])

    return {
        "summary": build_summary(series_df, item["metadata"]["granularity"]),
        "period_trends": period_trends,
        "trend_highlights": build_trend_highlights(period_trends),
        "festival_impact": build_festival_impact(enriched_df, item["metadata"]["granularity"]),
        "top_festivals": build_top_festivals(enriched_df),
        "top_products": build_product_leaderboard(item["metadata"]["product_summary"]),
        "selected_product_stats": build_selected_product_stats(
            item["metadata"]["product_summary"],
            resolved_product,
        ),
        "selected_product": resolved_product,
    }


def _chart_history(series_df: pd.DataFrame, granularity: str) -> list[dict[str, Any]]:
    history_limit = FREQUENCY_PROFILES[granularity]["history_limit"]
    history_df = series_df.tail(history_limit).copy()
    history_df["sales"] = history_df["sales"].round(2)
    return _serialize_dates(history_df.to_dict("records"))


def generate_forecast(
    item: dict[str, Any],
    calendar,
    selected_product: str | None = None,
    forecast_periods: int | None = None,
) -> dict[str, Any]:
    filtered_df, resolved_product = filter_dataset_by_product(item, selected_product)
    series_df = aggregate_sales_series(filtered_df)

    if len(series_df) < 2:
        raise ValueError("At least two data points are required to generate a forecast.")

    granularity = item["metadata"]["granularity"]
    profile = FREQUENCY_PROFILES[granularity]
    periods = forecast_periods or profile["default_periods"]
    periods = max(1, int(periods))

    prophet_df = series_df.rename(columns={"date": "ds", "sales": "y"}).copy()
    festival_features = calendar.add_festival_features(series_df.copy(), "date")
    festival_regressor = festival_features["days_to_festival"].apply(lambda value: 1 if abs(value) <= 7 else 0)
    use_festival_regressor = festival_regressor.nunique() > 1

    prophet_model = Prophet(
        daily_seasonality=profile["daily_seasonality"],
        weekly_seasonality=profile["weekly_seasonality"],
        yearly_seasonality=profile["yearly_seasonality"],
        interval_width=0.85,
    )

    if use_festival_regressor:
        prophet_df["festival_impact"] = festival_regressor.values
        prophet_model.add_regressor("festival_impact")

    prophet_model.fit(prophet_df)

    future = prophet_model.make_future_dataframe(
        periods=periods,
        freq=profile["prophet_freq"],
        include_history=True,
    )
    if use_festival_regressor:
        future_features = calendar.add_festival_features(pd.DataFrame({"date": future["ds"]}), "date")
        future["festival_impact"] = future_features["days_to_festival"].apply(
            lambda value: 1 if abs(value) <= 7 else 0
        )

    forecast_df = prophet_model.predict(future)
    future_only = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods).copy()
    future_only[["yhat", "yhat_lower", "yhat_upper"]] = future_only[
        ["yhat", "yhat_lower", "yhat_upper"]
    ].clip(lower=0)

    forecast_records = [
        {
            "date": row["ds"].date().isoformat(),
            "predicted_sales": _round_or_zero(row["yhat"]),
            "lower_bound": _round_or_zero(row["yhat_lower"]),
            "upper_bound": _round_or_zero(row["yhat_upper"]),
        }
        for _, row in future_only.iterrows()
    ]

    first_half = future_only["yhat"].head(max(1, len(future_only) // 2)).mean()
    second_half = future_only["yhat"].tail(max(1, len(future_only) // 2)).mean()
    projected_growth = _safe_growth(float(second_half), float(first_half)) if first_half else 0.0

    if projected_growth > 5:
        projected_direction = "upward"
    elif projected_growth < -5:
        projected_direction = "downward"
    else:
        projected_direction = "stable"

    peak_row = future_only.loc[future_only["yhat"].idxmax()]
    comparison_window = min(profile["comparison_window"], len(series_df))
    current_average_sales = float(series_df["sales"].tail(comparison_window).mean()) if comparison_window else 0.0
    latest_actual_sales = float(series_df["sales"].iloc[-1]) if not series_df.empty else 0.0
    average_predicted_sales = float(future_only["yhat"].mean())
    next_period_forecast = float(future_only["yhat"].iloc[0]) if not future_only.empty else 0.0

    return {
        "granularity": granularity,
        "selected_product": resolved_product,
        "forecast_periods": periods,
        "forecast_unit": profile["future_label"],
        "historical_series": _chart_history(series_df, granularity),
        "forecast": forecast_records,
        "summary": {
            "average_predicted_sales": _round_or_zero(average_predicted_sales),
            "cumulative_predicted_sales": _round_or_zero(future_only["yhat"].sum()),
            "peak_forecast_sales": _round_or_zero(peak_row["yhat"]),
            "peak_forecast_date": peak_row["ds"].date().isoformat(),
            "projected_growth_pct": projected_growth,
            "projected_direction": projected_direction,
            "current_average_sales": _round_or_zero(current_average_sales),
            "latest_actual_sales": _round_or_zero(latest_actual_sales),
            "comparison_to_current": {
                "baseline_window_points": comparison_window,
                "current_average_sales": _round_or_zero(current_average_sales),
                "forecast_average_sales": _round_or_zero(average_predicted_sales),
                "delta_sales": _round_or_zero(average_predicted_sales - current_average_sales),
                "delta_pct": _safe_growth(average_predicted_sales, current_average_sales)
                if current_average_sales > 0
                else 0.0,
                "next_period_forecast": _round_or_zero(next_period_forecast),
                "next_period_delta_pct": _safe_growth(next_period_forecast, latest_actual_sales)
                if latest_actual_sales > 0
                else 0.0,
            },
        },
    }


def read_uploaded_file(file_storage) -> pd.DataFrame:
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".csv"):
        return pd.read_csv(file_storage)
    if filename.endswith(".xlsx"):
        return pd.read_excel(file_storage, engine="openpyxl")
    raise ValueError("Unsupported file type. Please upload a CSV or XLSX file.")


class UploadStore:
    def __init__(self, ttl_minutes: int = 90, max_items: int = 25) -> None:
        self.ttl_minutes = ttl_minutes
        self.max_items = max_items
        self._items: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def _purge_expired_locked(self) -> None:
        cutoff = datetime.utcnow() - timedelta(minutes=self.ttl_minutes)
        expired_keys = [
            upload_id
            for upload_id, item in self._items.items()
            if item["created_at"] < cutoff
        ]
        for upload_id in expired_keys:
            self._items.pop(upload_id, None)

    def save(self, data: pd.DataFrame, metadata: dict[str, Any]) -> str:
        upload_id = uuid4().hex
        with self._lock:
            self._purge_expired_locked()
            if len(self._items) >= self.max_items:
                oldest_upload_id = min(
                    self._items.items(),
                    key=lambda item: item[1]["created_at"],
                )[0]
                self._items.pop(oldest_upload_id, None)

            self._items[upload_id] = {
                "data": data,
                "metadata": metadata,
                "created_at": datetime.utcnow(),
            }
        return upload_id

    def get(self, upload_id: str) -> dict[str, Any] | None:
        with self._lock:
            self._purge_expired_locked()
            return self._items.get(upload_id)

    def count(self) -> int:
        with self._lock:
            self._purge_expired_locked()
            return len(self._items)


def search_products(item: dict[str, Any], query: str = "", limit: int = 10) -> list[dict[str, Any]]:
    product_summary = item["metadata"]["product_summary"]
    if product_summary.empty:
        return []

    search_text = query.strip().lower()
    candidates = product_summary.copy()

    if search_text:
        mask = candidates["search_text"].fillna("").str.contains(search_text, regex=False)
        candidates = candidates.loc[mask].copy()

    if candidates.empty:
        return []

    candidates["starts_with"] = candidates["product_key"].astype(str).str.lower().str.startswith(search_text)
    candidates = candidates.sort_values(
        ["starts_with", "total_sales", "product_key"],
        ascending=[False, False, True],
    ).head(limit)

    return [
        {
            "value": row["product_key"],
            "total_sales": _round_or_zero(row["total_sales"]),
            "records": int(row["record_count"]),
            "rank": int(row["rank"]),
        }
        for _, row in candidates.iterrows()
    ]
