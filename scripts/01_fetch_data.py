import akshare as ak
import yfinance as yf
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
HISTORY_DIR = DATA_DIR / "history"


def _calc_weekly_return(df: pd.DataFrame, close_col: str) -> float:
    df = df.dropna(subset=[close_col]).tail(10)
    if len(df) < 6:
        raise ValueError("可用交易日不足 6 天，无法计算周涨跌幅")
    return (df[close_col].iloc[-1] / df[close_col].iloc[-6] - 1) * 100


def _get_last_close(df: pd.DataFrame, close_col: str) -> float:
    df = df.dropna(subset=[close_col])
    if df.empty:
        raise ValueError("未找到有效收盘价")
    return float(df[close_col].iloc[-1])


def _get_last_date(df: pd.DataFrame) -> str:
    if "date" in df.columns:
        return str(df["date"].iloc[-1])
    return str(df.index[-1])


def get_weekly_data():
    """获取本周主要指数和行业数据"""
    data = {}
    errors = []

    # A 股主要指数（使用 akshare）
    a_share_indices = {
        "上证指数": "sh000001",
        "深证成指": "sz399001",
        "创业板指": "sz399006",
    }

    for index_name, symbol in a_share_indices.items():
        try:
            index_df = ak.stock_zh_index_daily(symbol=symbol)
            weekly_return = _calc_weekly_return(index_df, "close")
            data[index_name] = {
                "close": _get_last_close(index_df, "close"),
                "change_pct": float(weekly_return),
                "date": _get_last_date(index_df),
                "source": "akshare.stock_zh_index_daily",
            }
        except Exception as e:
            message = f"{index_name}获取失败：{e}"
            print(message)
            errors.append(message)

    # 美股指数（使用 yfinance）
    us_indices = {
        "标普500": {"yf": "^GSPC", "ak": ".INX"},
        "纳斯达克": {"yf": "^IXIC", "ak": ".IXIC"},
    }

    for index_name, symbols in us_indices.items():
        try:
            us_df = yf.download(symbols["yf"], period="10d", progress=False)
            weekly_return = _calc_weekly_return(us_df, "Close")
            data[index_name] = {
                "close": _get_last_close(us_df, "Close"),
                "change_pct": float(weekly_return),
                "source": "yfinance",
            }
        except Exception as e:
            message = f"{index_name}获取失败：{e}"
            print(message)
            errors.append(message)

            try:
                backup_df = ak.index_us_stock_sina(symbol=symbols["ak"])
                close_col = "close" if "close" in backup_df.columns else "收盘"
                weekly_return = _calc_weekly_return(backup_df, close_col)
                data[index_name] = {
                    "close": _get_last_close(backup_df, close_col),
                    "change_pct": float(weekly_return),
                    "source": "akshare.index_us_stock_sina",
                }
                errors.append(f"{index_name}使用 akshare.index_us_stock_sina 备用接口获取")
            except Exception as backup_e:
                backup_message = f"{index_name}备用接口获取失败：{backup_e}"
                print(backup_message)
                errors.append(backup_message)

    # 申万行业（akshare）
    try:
        sw = ak.sw_index_daily_indicator(symbol="801010", indicator="近一周")
        # 实际字段名需根据接口返回调整
        data["sectors"] = sw.to_dict(orient="records")
    except Exception as e:
        message = f"行业数据获取失败：{e}"
        print(message)
        errors.append(message)

        try:
            flow = ak.stock_fund_flow_industry()
            flow = flow[["行业", "行业-涨跌幅"]].dropna().copy()
            flow["行业-涨跌幅"] = pd.to_numeric(flow["行业-涨跌幅"], errors="coerce")
            flow = flow.dropna().sort_values("行业-涨跌幅", ascending=False).head(8)
            data["sectors"] = [
                {
                    "rank": int(i + 1),
                    "name": str(row["行业"]),
                    "change_pct": float(row["行业-涨跌幅"]),
                    "source": "akshare.stock_fund_flow_industry",
                }
                for i, (_, row) in enumerate(flow.iterrows())
            ]
            errors.append("行业数据使用 akshare.stock_fund_flow_industry 备用接口获取")
        except Exception as backup_e:
            backup_message = f"行业备用接口获取失败：{backup_e}"
            print(backup_message)
            errors.append(backup_message)
            data["sectors"] = []

    data["errors"] = errors
    data["generated_at"] = datetime.now().isoformat(timespec="seconds")

    # 保存
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    output_file = DATA_DIR / "weekly_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    history_file = HISTORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_weekly_data.json"
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"数据获取完成：{len(data)} 个数据项")
    return data


if __name__ == "__main__":
    get_weekly_data()
