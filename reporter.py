import os
from datetime import datetime
from config import REPORT_DIR

SIGNAL_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}


def _signal_badge(analysis_text: str) -> str:
    for level in ("HIGH", "MEDIUM", "LOW"):
        if level in analysis_text:
            return f"{SIGNAL_EMOJI.get(level, '')} {level}"
    return "⚪ UNKNOWN"


def save_report(analyses: list[dict], synthesis: str) -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)

    now = datetime.now()
    week_num = now.isocalendar()[1]
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(REPORT_DIR, f"safetywatch_{timestamp}.md")

    lines = [
        f"# SafetyWatch 周报 | {now.strftime('%Y')} W{week_num:02d}",
        f"\n生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}  |  数据来源：openFDA\n",
        "---\n",
        "## 执行摘要\n",
        synthesis,
        "\n---\n",
        "## 各模块详细分析\n",
    ]

    for a in analyses:
        badge = _signal_badge(a["analysis"])
        lines.append(f"### {a['category']}  {badge}\n")
        lines.append(f"> 数据来源：{a['url']}\n")
        lines.append(a["analysis"])
        lines.append("\n---\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename
