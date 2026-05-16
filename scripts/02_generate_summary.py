import anthropic
import json
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _format_pct(value) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "暂无数据"


def build_local_summary(weekly_data: dict) -> str:
    """在没有 Claude API Key 时生成一段本地规则摘要。"""
    index_items = [
        (name, value)
        for name, value in weekly_data.items()
        if isinstance(value, dict) and "change_pct" in value
    ]
    sectors = weekly_data.get("sectors", [])

    if index_items:
        index_text = "，".join(
            f"{name}周涨跌幅为{_format_pct(value.get('change_pct'))}"
            for name, value in index_items
        )
    else:
        index_text = "主要指数数据暂不完整"

    if sectors:
        top_sectors = sectors[:3]
        sector_text = "，".join(
            f"{item.get('name', '未命名行业')}上涨{_format_pct(item.get('change_pct'))}"
            for item in top_sectors
        )
    else:
        sector_text = "行业涨跌幅数据暂未获取成功"

    return (
        f"本周市场表现呈现分化特征，{index_text}。从跨市场表现看，A 股与美股走势并不完全同步，"
        f"说明不同市场仍主要受各自流动性、盈利预期和风险偏好影响。行业层面，{sector_text}，"
        f"显示资金短期更关注景气度改善或政策预期较强的方向。后续一周可重点关注国内宏观数据、"
        f"上市公司业绩变化、美联储政策表态以及人民币汇率波动等因素。若外部风险偏好继续改善，"
        f"权益市场可能维持结构性机会；但若成交量不足或热点切换过快，指数仍可能以震荡整理为主。"
    )


def generate_market_summary(weekly_data: dict) -> str:
    """调用 Claude API 生成市场周报摘要。"""
    load_dotenv(PROJECT_ROOT / ".env")

    prompt = f"""
你是一名金融市场分析助理，请根据以下股市周度数据，生成一段 300-400 字的中文市场周报摘要。

周度数据：
{json.dumps(weekly_data, ensure_ascii=False, indent=2)}

写作要求：
1. 概括主要指数的涨跌表现。
2. 点评 2-3 个表现突出的行业。
3. 简要说明 A 股与美股表现差异。
4. 展望下周需要关注的市场因素。
5. 语言专业、客观、简洁。
6. 直接输出正文，不要标题，不要使用“根据数据”“如上所示”等套话。
"""

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        client = anthropic.Anthropic(api_key=anthropic_key)
        message = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()

    print("未检测到 ANTHROPIC_API_KEY，使用本地规则摘要。")
    return build_local_summary(weekly_data)


if __name__ == "__main__":
    with open(DATA_DIR / "weekly_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = generate_market_summary(data)
    print(summary)

    # 保存摘要
    with open(DATA_DIR / "ai_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
