"""Run the full weekly report pipeline and render Quarto outputs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(command))
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def render_format(fmt: str) -> bool:
    output_name = f"weekly_report.{fmt}"
    command = [
        "quarto",
        "render",
        "report_template.qmd",
        "--to",
        fmt,
        "--output-dir",
        "output",
        "--output",
        output_name,
    ]
    try:
        run(command)
        return True
    except FileNotFoundError:
        print("未找到 quarto 命令。请先安装 Quarto: https://quarto.org/docs/get-started/")
        return False
    except subprocess.CalledProcessError as exc:
        print(f"Quarto 渲染 {fmt} 失败，退出码: {exc.returncode}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch data, generate summary, and render the report.")
    parser.add_argument("--skip-fetch", action="store_true", help="Use existing data/weekly_data.json.")
    parser.add_argument("--skip-summary", action="store_true", help="Use existing data/ai_summary.txt.")
    parser.add_argument("--sample", action="store_true", help="Pass --sample to the data fetch script.")
    parser.add_argument("--formats", default="html,pdf", help="Comma-separated formats, e.g. html or html,pdf.")
    args = parser.parse_args()

    if not args.skip_fetch:
        fetch_command = [sys.executable, "scripts/01_fetch_data.py"]
        if args.sample:
            fetch_command.append("--sample")
        run(fetch_command)

    if not args.skip_summary:
        run([sys.executable, "scripts/02_generate_summary.py"])

    if not shutil.which("quarto"):
        print("未找到 quarto，已完成数据和摘要生成，但无法渲染报告。")
        sys.exit(1)

    formats = [item.strip() for item in args.formats.split(",") if item.strip()]
    results = {fmt: render_format(fmt) for fmt in formats}
    if not results.get("html", False):
        sys.exit(1)
    if "pdf" in results and not results["pdf"]:
        print("HTML 已生成；PDF 失败通常是 LaTeX/中文字体环境问题，可作为待完善项说明。")


if __name__ == "__main__":
    main()

