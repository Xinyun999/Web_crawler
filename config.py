import os
from dotenv import load_dotenv

load_dotenv()

# ── Azure OpenAI ──────────────────────────────────────────
AZURE_OAI_ENDPOINT   = os.getenv("AZURE_OAI_ENDPOINT")
AZURE_OAI_KEY        = os.getenv("AZURE_OAI_KEY")
AZURE_OAI_DEPLOYMENT = os.getenv("AZURE_OAI_DEPLOYMENT")

# ── openFDA API ───────────────────────────────────────────
FDA_API_BASE    = "https://api.fda.gov"
FDA_FETCH_LIMIT = 10   # 每个端点拉取的记录数
FDA_LOOKBACK_DAYS = 7  # 监控过去 N 天的数据

REPORT_DIR = "reports"

# ── LLM Prompts ───────────────────────────────────────────
PROMPT_ADVERSE_EVENTS = """
你是 Genentech SMPS 团队的药品安全分析师。
以下是过去 7 天来自 openFDA 的严重药品不良事件记录，请用中文分析：

【信号强度】：HIGH / MEDIUM / LOW（根据事件数量与严重程度判断）
【受影响药物类别】：列出涉及的主要药物或类别
【关键不良反应】：3-5 条最常见或最严重的反应（每条以 - 开头）
【风险提示】：是否存在值得关注的安全信号？简述理由

数据：
{text}
"""

PROMPT_RECALLS = """
你是 Genentech SMPS 团队的法规合规分析师。
以下是来自 openFDA 的当前进行中的药品召回记录，请用中文分析：

【信号强度】：HIGH / MEDIUM / LOW（根据召回级别与原因判断）
【主要召回原因】：归纳 2-3 类主要问题（如无菌问题、标签错误、杂质超标）
【关键记录】：3-5 条最重要的召回事件（每条以 - 开头）
【合规建议】：对内部生产/质控有何参考意义？

数据：
{text}
"""

PROMPT_LABELS = """
你是 Genentech SMPS 团队的医学事务分析师。
以下是来自 openFDA 含有 Black Box Warning 的药品标签记录，请用中文分析：

【信号强度】：HIGH / MEDIUM / LOW（根据警告严重程度判断）
【涉及药物】：列出品牌名和主要适应症
【Black Box 警告摘要】：3-5 条核心警告内容（每条以 - 开头）
【对在研分子的参考价值】：该类警告对同靶点/同机制在研分子有何启示？

数据：
{text}
"""

PROMPT_SYNTHESIS = """
你是 Genentech SMPS 团队的首席安全情报分析师。
以下是本周 SafetyWatch Agent 对三类 openFDA 数据的分析结果，请生成执行摘要：

【本周安全态势总结】：2-3 句概述本周整体风险水平
【优先关注事项】：按重要性列出 3 条行动建议（格式：- [ ] 行动项）
【需人工复核的信号】：哪些发现建议提交安全官员审核？

各模块分析结果：
{analyses}
"""
