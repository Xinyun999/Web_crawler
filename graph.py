from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from crawler import crawl_all
from summarizer import summarize_all
from reporter import save_report
from rag import get_rag
from storage import save_run
from tools import send_safety_alert


class AgentState(TypedDict, total=False):
    raw_data:       List[Dict]
    rag_contexts:   Dict[str, str]
    analyses:       List[Dict]
    synthesis:      str
    overall_signal: str
    report_path:    str
    flags:          List[str]


# ── Nodes ─────────────────────────────────────────────────

def crawl_node(state: AgentState) -> AgentState:
    print("\n  [1] crawl_node — 拉取 openFDA 数据")
    return {"raw_data": crawl_all()}


def rag_node(state: AgentState) -> AgentState:
    print("\n  [2] rag_node — 检索内部分子知识库 (ChromaDB)")
    rag = get_rag()
    contexts = {}
    for item in state["raw_data"]:
        query = f"{item['category']} {item['text'][:300]}"
        contexts[item["category"]] = rag.retrieve(query)
    return {"rag_contexts": contexts}


def analyze_node(state: AgentState) -> AgentState:
    print("\n  [3] analyze_node — LLM 信号分析 (RAG 增强)")
    enriched = []
    for item in state["raw_data"]:
        ctx = state.get("rag_contexts", {}).get(item["category"], "")
        e = dict(item)
        if ctx and not item["error"]:
            e["text"] = (
                f"【内部相关分子参考（RAG 检索）】\n{ctx}\n\n"
                f"【openFDA 数据】\n{item['text']}"
            )
        enriched.append(e)

    analyses, synthesis = summarize_all(enriched)
    return {"analyses": analyses, "synthesis": synthesis}


def signal_check_node(state: AgentState) -> AgentState:
    print("\n  [4] signal_check_node — 评估整体信号强度")
    priority = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
    max_level = "LOW"
    flags = []

    for a in state["analyses"]:
        for level in ("HIGH", "MEDIUM", "LOW"):
            if level in a["analysis"]:
                if priority[level] > priority[max_level]:
                    max_level = level
                if level == "HIGH":
                    flags.append(f"⚠️  {a['category']} 检测到 HIGH 信号，建议安全官员复核")
                break

    return {"overall_signal": max_level, "flags": flags}


def escalate_node(state: AgentState) -> AgentState:
    """HIGH 信号时触发的 HITL 门控节点（当前自动标记，生产可改为 await 人工确认）。"""
    print("\n  [5-HITL] escalate_node — HIGH 信号已标记，等待人工复核...")
    for flag in state.get("flags", []):
        print(f"         {flag}")
    return {}


def store_node(state: AgentState) -> AgentState:
    print("\n  [5] store_node — 写入 SQLite")
    save_run(state["analyses"], report_path="pending")
    return {}


def report_node(state: AgentState) -> AgentState:
    print("\n  [6] report_node — 生成 Markdown 报告")
    path = save_report(state["analyses"], state["synthesis"])
    return {"report_path": path}


def notify_node(state: AgentState) -> AgentState:
    print("\n  [7] notify_node — MCP 工具通知")
    flags = state.get("flags", [])
    msg = (
        f"SafetyWatch 周报已生成\n"
        f"整体信号强度: {state.get('overall_signal', 'N/A')}\n"
        f"报告路径: {state.get('report_path', '')}"
    )
    if flags:
        msg += "\n\n需关注:\n" + "\n".join(flags)

    result = send_safety_alert.invoke({"message": msg})
    print(f"         {result}")
    return {}


# ── 条件边：HIGH 信号走 escalate，否则直接 store ──────────

def route_signal(state: AgentState) -> str:
    return "escalate" if state.get("overall_signal") == "HIGH" else "store"


# ── 构建图 ────────────────────────────────────────────────

def build_graph():
    g = StateGraph(AgentState)

    g.add_node("crawl",        crawl_node)
    g.add_node("rag",          rag_node)
    g.add_node("analyze",      analyze_node)
    g.add_node("signal_check", signal_check_node)
    g.add_node("escalate",     escalate_node)
    g.add_node("store",        store_node)
    g.add_node("report",       report_node)
    g.add_node("notify",       notify_node)

    g.set_entry_point("crawl")
    g.add_edge("crawl",        "rag")
    g.add_edge("rag",          "analyze")
    g.add_edge("analyze",      "signal_check")
    g.add_conditional_edges(
        "signal_check",
        route_signal,
        {"escalate": "escalate", "store": "store"},
    )
    g.add_edge("escalate",     "store")
    g.add_edge("store",        "report")
    g.add_edge("report",       "notify")
    g.add_edge("notify",       END)

    return g.compile()
