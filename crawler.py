import requests
from datetime import datetime, timedelta
from config import FDA_API_BASE, FDA_FETCH_LIMIT, FDA_LOOKBACK_DAYS


def _get(url: str) -> dict | None:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _date_range() -> tuple[str, str]:
    end = datetime.now()
    start = end - timedelta(days=FDA_LOOKBACK_DAYS)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


# ── 1. 药品不良事件（严重事件，最近 N 天） ────────────────
def fetch_adverse_events() -> dict:
    start, end = _date_range()
    url = (f"{FDA_API_BASE}/drug/event.json"
           f"?search=serious:1+AND+receivedate:[{start}+TO+{end}]"
           f"&limit={FDA_FETCH_LIMIT}&sort=receivedate:desc")

    data = _get(url)
    if "error" in data:
        return {"category": "药品不良事件", "url": url, "text": "", "error": data["error"]}

    records = data.get("results", [])
    lines = []
    for i, r in enumerate(records, 1):
        drugs = [d.get("medicinalproduct", "未知") for d in r.get("patient", {}).get("drug", [])[:3]]
        reactions = [rx.get("reactionmeddrapt", "") for rx in r.get("patient", {}).get("reaction", [])[:4]]
        serious_type = "死亡" if r.get("seriousnessdeath") == 1 else \
                       "住院" if r.get("seriousnesshospitalization") == 1 else "其他严重"
        lines.append(
            f"[{i}] 日期:{r.get('receivedate','')} | 严重类型:{serious_type}\n"
            f"    药品: {', '.join(drugs)}\n"
            f"    不良反应: {', '.join(reactions)}"
        )

    return {"category": "药品不良事件", "url": url,
            "text": "\n\n".join(lines), "error": None}


# ── 2. 药品召回（进行中） ─────────────────────────────────
def fetch_recalls() -> dict:
    url = (f"{FDA_API_BASE}/drug/enforcement.json"
           f"?search=status:\"Ongoing\""
           f"&limit={FDA_FETCH_LIMIT}&sort=recall_initiation_date:desc")

    data = _get(url)
    if "error" in data:
        return {"category": "药品召回", "url": url, "text": "", "error": data["error"]}

    records = data.get("results", [])
    lines = []
    for i, r in enumerate(records, 1):
        lines.append(
            f"[{i}] 厂商: {r.get('recalling_firm', '')}\n"
            f"    产品: {r.get('product_description', '')[:150]}\n"
            f"    召回原因: {r.get('reason_for_recall', '')[:200]}\n"
            f"    召回级别: {r.get('classification', '')} | 日期: {r.get('recall_initiation_date', '')}"
        )

    return {"category": "药品召回", "url": url,
            "text": "\n\n".join(lines), "error": None}


# ── 3. 药品标签（含 Black Box Warning） ───────────────────
def fetch_labels() -> dict:
    url = (f"{FDA_API_BASE}/drug/label.json"
           f"?search=_exists_:boxed_warning"
           f"&limit={FDA_FETCH_LIMIT}")

    data = _get(url)
    if "error" in data:
        return {"category": "药品标签", "url": url, "text": "", "error": data["error"]}

    records = data.get("results", [])
    lines = []
    for i, r in enumerate(records, 1):
        openfda = r.get("openfda", {})
        brand = openfda.get("brand_name", ["未知"])[0]
        indication = r.get("indications_and_usage", [""])[0][:200]
        boxed = r.get("boxed_warning", [""])[0][:300]
        lines.append(
            f"[{i}] 品牌名: {brand}\n"
            f"    适应症: {indication}\n"
            f"    Black Box Warning: {boxed}"
        )

    return {"category": "药品标签", "url": url,
            "text": "\n\n".join(lines), "error": None}


# ── 入口 ──────────────────────────────────────────────────
def crawl_all() -> list[dict]:
    print("  → 药品不良事件...")
    adverse = fetch_adverse_events()
    print("  → 药品召回...")
    recalls = fetch_recalls()
    print("  → 药品标签 (Black Box Warning)...")
    labels = fetch_labels()
    return [adverse, recalls, labels]
