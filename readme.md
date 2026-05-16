# T-E2：AI Agent 自动生成股市周报（PDF + HTML）

| 项目 | 内容 |
| --- | --- |
| 课程 | 数据分析与经济决策（ds2026） |
| 题目 | T-E2：AI Agent 自动生成股市周报（PDF + HTML） |
| 小组 | 第 6 组 |
| 成员 | 杨鹏飞（25210278）、况达（25210151）、刘苹苹（25210194）、姚尚彤（25210281）、林佩敏（25210184）、邓佳鸣（25210124）、劳润杰（25210154）、方少娜（25210129） |
| GitHub | https://github.com/ypengfei36-commits/ds2026-G06-weekly-market-report |
| Pages | https://ypengfei36-commits.github.io/ds2026-G06-weekly-market-report/ |
| 日期 | 2026-05-16 |

## 项目简介

本项目按照 T-E2 题目要求，构建一个自动化股市周报生成系统：脚本自动获取 A 股和美股主要指数、行业涨跌幅数据，生成市场摘要，并使用 Quarto 输出 HTML 与 PDF 两种格式的周报。

当前自动获取的主要指数包括：上证指数、深证成指、创业板指、标普500、纳斯达克。若部分数据源临时限流或接口字段变化，脚本会记录异常，并尽量使用备用接口完成报告生成。

## 目录结构

```text
T-E2_WeeklyReport/
├── readme.md
├── _quarto.yml
├── requirements.txt
├── .gitignore
├── .env.example
├── report_template.qmd
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
├── demo_static/
│   └── demo_report.qmd
└── .github/
    └── workflows/
        └── weekly_report.yml
```

## 运行方式

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

一键生成正式周报：

```powershell
python scripts/03_render_report.py
```

也可以分步运行：

```powershell
python scripts/01_fetch_data.py
python scripts/02_generate_summary.py
quarto render report_template.qmd --to html
quarto render report_template.qmd --to pdf
```

最终报告输出在：

- `output/weekly_report.html`
- `output/weekly_report.pdf`

## 成员分工

| 协作模块 | 成员 | 内容 |
| --- | --- | --- |
| 项目整合与仓库维护 | 杨鹏飞、况达 | 项目结构整理、仓库维护、运行流程检查 |
| 数据获取与数据结构整理 | 刘苹苹、姚尚彤 | 数据源梳理、字段结构统一、异常情况记录 |
| Quarto 报告模板与页面呈现 | 林佩敏、劳润杰 | 报告模板设计、图表呈现、HTML/PDF 输出检查 |
| AI 摘要生成与结果复核 | 邓佳鸣、方少娜 | 摘要提示词整理、AI 输出复核、结果解释完善 |
| 测试运行与提交整理 | 全体成员 | 本地运行测试、报告内容检查、最终材料整理 |

## AI 工具使用说明

### 使用的 AI 工具

- ChatGPT/Codex：用于理解题目要求、拆解项目阶段、生成项目骨架、辅助编写 README 和代码。
- Claude API：脚本支持通过 `ANTHROPIC_API_KEY` 调用 Claude 生成市场摘要；本地未配置 Key 时使用规则摘要保证流程可复现。

### AI 辅助过程记录与问题处理

| 阶段 | 向 AI 提问的内容 | AI 辅助结果 | 遇到的坑与处理 |
| --- | --- | --- | --- |
| 作业理解 | 解释 T-E2 题目要求，并结合提交要求拆解步骤 | 得到阶段式实施方案 | 起初把普通项目目录结构也纳入计划，后来确认 E 类题目以 T-E2 目录为准 |
| 执行节奏 | 将项目拆成按阶段推进、每阶段暂停核对的流程 | 明确 Phase 1 至 Phase 8 的执行顺序 | 起初把 PDF 作为增强项，后来确认 PDF 与 HTML 都是必要交付物 |
| 数据接口 | 如何用 akshare 和 yfinance 获取指数、行业数据 | 完成自动数据获取脚本 | yfinance 出现限流，部分 akshare 示例接口不可用，改为记录错误并使用备用接口 |
| 报告生成 | 如何用 Quarto 读取 JSON 并输出 HTML/PDF | 完成正式报告模板和一键运行脚本 | PDF 中文渲染需要 TinyTeX/ctex 支持，最终使用 `ctexart` 配置生成 |
| README 编写 | 根据小组信息、仓库地址和项目目标生成 README | 得到项目简介、目录结构、成员分工和运行说明 | AI 工具说明最初写得过泛，后改为记录具体工具和提问过程 |

## GitHub Actions 与 Pages

仓库包含 `.github/workflows/weekly_report.yml`，支持手动触发和每周五北京时间 16:00 自动触发。工作流会安装依赖、生成 HTML/PDF，并将 HTML 发布到 GitHub Pages，同时把 PDF 保留为 workflow artifact。

## 提交说明

最终提交物包括：

- GitHub 仓库完整代码。
- GitHub Pages 在线报告。
- `output/weekly_report.html`
- `output/weekly_report.pdf`
- 打包文件：`ds2026_G06_T-E2_杨鹏飞.zip`
