"""Generate a weekly market summary with an LLM or a local fallback."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "weekly_data.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "ai_summary.txt"


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except Exception:
        env_path = PROJECT_ROOT / ".env"
        if not env_path.exists():
            return
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def build_prompt(data: dict[str, Any]) -> str:
    return f"""
你是一位专业的金融分析师。请根据以下本周市场数据，撰写一段 300-400 字的中文市场周报摘要。

本周数据：
{json.dumps(data, ensure_ascii=False, indent=2)}

要求：
1. 概括主要指数涨跌情况。
2. 点评 2-3 个表现突出的行业及可能原因。
3. 简要展望下周需要关注的因素。
4. 不要使用“根据数据”“如上所示”等套话。
5. 不要编造输入数据中不存在的指数、行业、数值或事件。
6. 直接输出正文，不需要标题。
""".strip()


def call_anthropic(prompt: str) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=1000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        print(f"Claude 摘要生成失败，改用本地摘要: {exc}")
        return None


def call_openai(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": "你是严谨、客观的金融市场周报撰写助手。"},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"OpenAI 摘要生成失败，改用本地摘要: {exc}")
        return None


def local_summary(data: dict[str, Any]) -> str:
    indices = data.get("indices", [])
    sectors = data.get("sectors", [])
    metadata = data.get("metadata", {})

    up_indices = [row for row in indices if float(row.get("change_pct", 0)) >= 0]
    down_indices = [row for row in indices if float(row.get("change_pct", 0)) < 0]
    sorted_indices = sorted(indices, key=lambda row: float(row.get("change_pct", 0)), reverse=True)
    sorted_sectors = sorted(sectors, key=lambda row: float(row.get("change_pct", 0)), reverse=True)

    strongest_index = sorted_indices[0] if sorted_indices else {"name": "主要指数", "change_pct": 0}
    weakest_index = sorted_indices[-1] if sorted_indices else {"name": "主要指数", "change_pct": 0}
    top_sector_names = "、".join(row.get("name", "") for row in sorted_sectors[:3]) or "优势行业"
    weak_sector_names = "、".join(row.get("name", "") for row in sorted_sectors[-2:]) or "弱势行业"
    week_start = metadata.get("week_start", "本周初")
    week_end = metadata.get("week_end", "本周末")

    return (
        f"{week_start} 至 {week_end}，主要市场指数整体呈现结构性分化。"
        f"纳入观察的 {len(indices)} 个指数中，{len(up_indices)} 个上涨、{len(down_indices)} 个下跌；"
        f"{strongest_index.get('name')}表现相对靠前，周涨跌幅为 {float(strongest_index.get('change_pct', 0)):.2f}%，"
        f"{weakest_index.get('name')}相对偏弱，周涨跌幅为 {float(weakest_index.get('change_pct', 0)):.2f}%。"
        f"行业层面，{top_sector_names}涨幅居前，反映资金对科技成长、产业升级或景气改善方向仍有关注；"
        f"{weak_sector_names}等板块表现靠后，说明部分顺周期和消费链条仍承压。"
        "下周可重点关注国内政策预期、上市公司业绩线索、海外利率变化、人民币汇率以及成交量能否持续放大。"
        "总体看，自动化数据能够较快捕捉市场变化，但摘要仍需要人工复核，尤其要检查接口异常、样本数据替代和 AI 可能产生的过度解释。"
    )


def generate_market_summary(data: dict[str, Any]) -> str:
    prompt = build_prompt(data)
    return call_anthropic(prompt) or call_openai(prompt) or local_summary(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the AI market summary.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    load_dotenv_if_available()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    summary = generate_market_summary(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary + "\n", encoding="utf-8")
    print(f"摘要已保存: {args.output}")


if __name__ == "__main__":
    main()

