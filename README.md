# T-E2：AI Agent 自动生成股市周报

| 项目 | 内容 |
| --- | --- |
| 课程 | 数据分析与经济决策（ds2026） |
| 题目 | T-E2：AI Agent 自动生成股市周报（PDF + HTML） |
| 小组 | 第 6 组 |
| 成员 | 杨鹏飞（25210278）、况达（25210151）、刘苹苹（25210194）、姚尚彤（25210281）、林佩敏（25210184）、邓佳鸣（25210124）、劳润杰（25210154）、方少娜（25210129） |
| GitHub | https://github.com/ypengfei36-commits/ds2026-G06-weekly-market-report |
| Pages | https://ypengfei36-commits.github.io/ds2026-G06-weekly-market-report/ |
| 日期 | 2026-05-14 |

## 项目简介

本项目构建了一个自动化股市周报生成流程：先用 Python 获取 A 股和美股核心指数、行业表现数据，再调用 Claude 或 OpenAI API 生成中文市场摘要，最后通过 Quarto 渲染为 HTML/PDF 报告。若在线数据源或 API Key 不可用，项目会自动使用示例数据和本地规则摘要，保证演示和评分时流程可复现。

## 目录结构

```text
T-E2_WeeklyReport/
├── readme.md
├── _quarto.yml
├── requirements.txt
├── report_template.qmd
├── demo_static/
│   └── demo_report.qmd
├── scripts/
│   ├── 01_fetch_data.py
│   ├── 02_generate_summary.py
│   └── 03_render_report.py
├── data/
│   ├── weekly_data.json
│   ├── ai_summary.txt
│   └── history/
├── output/
│   ├── weekly_report.html
│   └── weekly_report.pdf
└── .github/
    └── workflows/
        └── weekly_report.yml
```

## 快速运行

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

先跑静态版，验证 Quarto 环境：

```bash
quarto render demo_static/demo_report.qmd --to html
```

跑完整流程：

```bash
python scripts/03_render_report.py --sample --formats html
```

连接真实数据源后运行：

```bash
python scripts/01_fetch_data.py
python scripts/02_generate_summary.py
quarto render report_template.qmd --to html --output-dir output --output weekly_report.html
```

如果本机 LaTeX/中文字体环境可用，可以额外生成 PDF：

```bash
quarto render report_template.qmd --to pdf --output-dir output --output weekly_report.pdf
```

## 数据说明

`data/weekly_data.json` 使用统一结构：

- `metadata`：项目名称、报告区间、生成时间、数据来源。
- `indices`：指数名称、市场、收盘价、周涨跌幅、日期、来源。
- `sectors`：行业排名、行业名称、涨跌幅、来源。
- `errors`：数据获取失败或降级使用示例数据的记录。

主要数据源：

- A 股指数：`akshare.stock_zh_index_daily`
- A 股行业：`akshare.stock_board_industry_name_em`
- 美股指数：`yfinance.download`

## AI 使用说明

本项目允许使用 Claude 或 OpenAI 生成市场摘要。开发时将密钥写入本地 `.env` 文件，不提交到仓库：

```text
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

如果没有 API Key，`scripts/02_generate_summary.py` 会自动生成一段规则摘要，便于完整跑通报告。最终报告中的 AI 摘要需要人工复核，重点检查是否出现捏造数据、过度解释或遗漏接口错误。

## 成员分工

| 角色 | 成员 | 工作内容 |
| --- | --- | --- |
| 项目整合与仓库维护 | 杨鹏飞、况达 | 项目结构整理、GitHub 仓库维护、运行流程检查 |
| 数据获取与数据结构整理 | 刘苹苹、姚尚彤 | 数据源梳理、字段结构统一、异常情况记录 |
| Quarto 报告模板与页面呈现 | 林佩敏、劳润杰 | 报告模板设计、图表呈现、HTML/PDF 输出检查 |
| AI 摘要生成与结果复核 | 邓佳鸣、方少娜 | 摘要提示词整理、AI 输出复核、结果解释完善 |
| 测试运行与提交整理 | 全体成员 | 本地运行测试、报告内容检查、最终材料整理 |

## 结果解读

本项目输出的周报不构成投资建议。自动化流程适合快速形成市场概览，但在实际工作中仍需要处理数据授权、接口稳定性、发布时间差异、模型输出合规和人工复核等问题。

## 提交清单

- GitHub 仓库地址和 GitHub Pages 地址已写入 readme。
- `data/weekly_data.json` 可复现生成。
- `data/ai_summary.txt` 可复现生成。
- `output/weekly_report.html` 能正常打开。
- PDF 若因本机 LaTeX 环境失败，已在报告/答辩中说明原因。
- readme 中已注明 AI 工具使用方式和成员分工。
