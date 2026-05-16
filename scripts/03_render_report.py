import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


def find_quarto() -> str:
    quarto_from_env = os.environ.get("QUARTO_BIN")
    if quarto_from_env:
        return quarto_from_env

    quarto_from_path = shutil.which("quarto")
    if quarto_from_path:
        return quarto_from_path

    default_windows_path = Path(r"C:\Program Files\Quarto\bin\quarto.exe")
    if default_windows_path.exists():
        return str(default_windows_path)

    raise FileNotFoundError(
        "Quarto was not found. Please install Quarto or set QUARTO_BIN."
    )


def run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"\n[START] {name}")
    print(" ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True)
    print(f"[DONE] {name}")


def main() -> None:
    env = os.environ.copy()
    env["QUARTO_PYTHON"] = str(PYTHON)

    quarto = find_quarto()

    steps = [
        (
            "Fetch market data",
            [str(PYTHON), str(PROJECT_ROOT / "scripts" / "01_fetch_data.py")],
        ),
        (
            "Generate AI summary",
            [str(PYTHON), str(PROJECT_ROOT / "scripts" / "02_generate_summary.py")],
        ),
        (
            "Render HTML report",
            [quarto, "render", "report_template.qmd", "--to", "html"],
        ),
        (
            "Render PDF report",
            [quarto, "render", "report_template.qmd", "--to", "pdf"],
        ),
    ]

    try:
        for name, command in steps:
            run_step(name, command, env=env)
    except subprocess.CalledProcessError as exc:
        print(f"\n[FAILED] {name}")
        print(f"Exit code: {exc.returncode}")
        if "PDF" in name:
            print("PDF rendering failed. Check the LaTeX/TinyTeX output above.")
        raise SystemExit(exc.returncode)
    except FileNotFoundError as exc:
        print(f"\n[FAILED] {exc}")
        raise SystemExit(1)

    html_file = PROJECT_ROOT / "output" / "weekly_report.html"
    pdf_file = PROJECT_ROOT / "output" / "weekly_report.pdf"

    print("\nAll steps completed.")
    print(f"HTML: {html_file}")
    print(f"PDF:  {pdf_file}")


if __name__ == "__main__":
    main()
