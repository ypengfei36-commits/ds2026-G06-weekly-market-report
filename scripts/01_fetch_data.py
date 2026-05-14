"""Fetch weekly A-share and US equity index data.

The script prefers live data from akshare/yfinance, but falls back to bundled
sample data when dependencies, network access, or remote APIs fail. This keeps
the assignment reproducible during demos.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "weekly_data.json"
CN_TZ = timezone(timedelta(hours=8))


SAMPLE_INDICES = [
    {"name": "上证指数", "market": "A股", "close": 3321.5, "change_pct": 1.23, "source": "sample"},
    {"name": "深证成指", "market": "A股", "close": 10543.2, "change_pct": 0.87, "source": "sample"},
    {"name": "创业板指", "market": "A股", "close": 2156.8, "change_pct": -0.45, "source": "sample"},
    {"name": "标普500", "market": "美股", "close": 5432.1, "change_pct": 2.15, "source": "sample"},
    {"name": "纳斯达克", "market": "美股", "close": 17654.3, "change_pct": 3.21, "source": "sample"},
]

SAMPLE_SECTORS = [
    {"rank": 1, "name": "通信", "change_pct": 4.5, "source": "sample"},
    {"rank": 2, "name": "电子", "change_pct": 3.2, "source": "sample"},
    {"rank": 3, "name": "计算机", "change_pct": 2.8, "source": "sample"},
    {"rank": 4, "name": "汽车", "change_pct": 1.5, "source": "sample"},
    {"rank": 5, "name": "医药", "change_pct": 0.3, "source": "sample"},
    {"rank": 6, "name": "银行", "change_pct": -0.5, "source": "sample"},
    {"rank": 7, "name": "地产", "change_pct": -1.2, "source": "sample"},
    {"rank": 8, "name": "食品饮料", "change_pct": -2.1, "source": "sample"},
]


def now_cn() -> datetime:
    return datetime.now(CN_TZ)


def pct_change(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("not enough observations to calculate weekly return")
    start = values[-6] if len(values) >= 6 else values[0]
    end = values[-1]
    if start == 0:
        raise ValueError("starting value is zero")
    return (end / start - 1) * 100


def clean_date(value: Any) -> str:
    text = str(value)
    return text[:10] if len(text) >= 10 else text


def fetch_a_share_indices(errors: list[str]) -> list[dict[str, Any]]:
    try:
        import akshare as ak
    except Exception as exc:  # pragma: no cover - depends on local env
        errors.append(f"akshare import failed: {exc}")
        return []

    index_specs = [
        ("上证指数", "sh000001"),
        ("深证成指", "sz399001"),
        ("创业板指", "sz399006"),
    ]
    rows: list[dict[str, Any]] = []

    for name, symbol in index_specs:
        try:
            frame = ak.stock_zh_index_daily(symbol=symbol).tail(10).copy()
            if "close" not in frame.columns:
                raise KeyError("missing close column")
            closes = [float(v) for v in frame["close"].dropna().tolist()]
            date_value = frame["date"].iloc[-1] if "date" in frame.columns else frame.index[-1]
            rows.append(
                {
                    "name": name,
                    "market": "A股",
                    "close": round(closes[-1], 2),
                    "change_pct": round(pct_change(closes), 2),
                    "date": clean_date(date_value),
                    "source": "akshare.stock_zh_index_daily",
                }
            )
        except Exception as exc:  # pragma: no cover - depends on remote API
            errors.append(f"{name} fetch failed: {exc}")

    return rows


def fetch_us_indices(errors: list[str]) -> list[dict[str, Any]]:
    try:
        import yfinance as yf
    except Exception as exc:  # pragma: no cover - depends on local env
        errors.append(f"yfinance import failed: {exc}")
        return []

    index_specs = [
        ("标普500", "^GSPC"),
        ("纳斯达克", "^IXIC"),
    ]
    rows: list[dict[str, Any]] = []

    for name, ticker in index_specs:
        try:
            frame = yf.download(ticker, period="10d", progress=False, auto_adjust=False)
            if frame.empty:
                raise ValueError("empty yfinance response")
            close = frame["Close"]
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            closes = [float(v) for v in close.dropna().tolist()]
            rows.append(
                {
                    "name": name,
                    "market": "美股",
                    "close": round(closes[-1], 2),
                    "change_pct": round(pct_change(closes), 2),
                    "date": clean_date(frame.index[-1]),
                    "source": "yfinance.download",
                }
            )
        except Exception as exc:  # pragma: no cover - depends on remote API
            errors.append(f"{name} fetch failed: {exc}")

    return rows


def fetch_sectors(errors: list[str]) -> list[dict[str, Any]]:
    try:
        import akshare as ak
    except Exception as exc:  # pragma: no cover - depends on local env
        errors.append(f"sector akshare import failed: {exc}")
        return []

    try:
        frame = ak.stock_board_industry_name_em()
        name_col = "板块名称"
        change_col = "涨跌幅"
        if name_col not in frame.columns or change_col not in frame.columns:
            raise KeyError(f"expected columns {name_col}/{change_col}, got {list(frame.columns)}")

        top = frame[[name_col, change_col]].dropna().copy()
        top[change_col] = top[change_col].astype(float)
        top = top.sort_values(change_col, ascending=False).head(8).reset_index(drop=True)
        return [
            {
                "rank": int(i + 1),
                "name": str(row[name_col]),
                "change_pct": round(float(row[change_col]), 2),
                "source": "akshare.stock_board_industry_name_em",
            }
            for i, row in top.iterrows()
        ]
    except Exception as exc:  # pragma: no cover - depends on remote API
        errors.append(f"sector fetch failed: {exc}")
        return []


def build_sample_payload(errors: list[str] | None = None) -> dict[str, Any]:
    today = now_cn().date()
    week_start = today - timedelta(days=6)
    indices = [{**row, "date": str(today)} for row in SAMPLE_INDICES]
    return {
        "metadata": {
            "project": "T-E2 AI Agent 自动生成股市周报",
            "report_title": "A 股与美股市场周报",
            "week_start": str(week_start),
            "week_end": str(today),
            "generated_at": now_cn().isoformat(timespec="seconds"),
            "data_sources": ["sample_data_for_demo"],
            "notes": "Live data was unavailable or --sample was used; bundled sample data is used for a reproducible demo.",
        },
        "indices": indices,
        "sectors": SAMPLE_SECTORS,
        "errors": errors or [],
    }


def get_weekly_data(use_sample: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    if use_sample:
        return build_sample_payload(errors)

    indices = fetch_a_share_indices(errors) + fetch_us_indices(errors)
    sectors = fetch_sectors(errors)

    if not indices:
        errors.append("all live index fetches failed; using sample indices")
        indices = [{**row, "date": str(now_cn().date())} for row in SAMPLE_INDICES]
    if not sectors:
        errors.append("all live sector fetches failed; using sample sectors")
        sectors = SAMPLE_SECTORS

    sources = sorted({row.get("source", "unknown") for row in indices + sectors})
    today = now_cn().date()
    return {
        "metadata": {
            "project": "T-E2 AI Agent 自动生成股市周报",
            "report_title": "A 股与美股市场周报",
            "week_start": str(today - timedelta(days=6)),
            "week_end": str(today),
            "generated_at": now_cn().isoformat(timespec="seconds"),
            "data_sources": sources,
            "notes": "If errors are present, the affected fields used fallback sample data.",
        },
        "indices": indices,
        "sectors": sectors,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch weekly market data for the Quarto report.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sample", action="store_true", help="Use bundled sample data instead of online APIs.")
    args = parser.parse_args()

    payload = get_weekly_data(use_sample=args.sample)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"数据已保存: {args.output}")
    print(f"指数数量: {len(payload['indices'])}; 行业数量: {len(payload['sectors'])}; 错误数量: {len(payload['errors'])}")


if __name__ == "__main__":
    main()

