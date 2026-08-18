from datetime import datetime
from langchain_core.tools import tool
from storage import get_history


@tool
def send_safety_alert(message: str) -> str:
    """Send a safety alert notification to the team (appends to notifications.log)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] SAFETY ALERT\n{message}\n{'='*60}\n"
    with open("notifications.log", "a", encoding="utf-8") as f:
        f.write(entry)
    return f"通知已写入 notifications.log"


@tool
def get_signal_history(days: int = 30) -> str:
    """Retrieve historical safety signal levels from SQLite database."""
    rows = get_history(days)
    if not rows:
        return "暂无历史记录"
    lines = [f"{r[0][:10]}  {r[1]:<10}  {r[2]}" for r in rows]
    header = f"{'日期':<10}  {'数据类别':<10}  信号强度\n" + "-" * 40
    return header + "\n" + "\n".join(lines)


MCP_TOOLS = [send_safety_alert, get_signal_history]
