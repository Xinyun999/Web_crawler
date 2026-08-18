from openai import AzureOpenAI
from config import (AZURE_OAI_ENDPOINT, AZURE_OAI_KEY, AZURE_OAI_DEPLOYMENT,
                    PROMPT_ADVERSE_EVENTS, PROMPT_RECALLS, PROMPT_LABELS, PROMPT_SYNTHESIS)

client = AzureOpenAI(
    azure_endpoint=AZURE_OAI_ENDPOINT,
    api_key=AZURE_OAI_KEY,
    api_version="2024-12-01-preview",
)

PROMPT_MAP = {
    "药品不良事件": PROMPT_ADVERSE_EVENTS,
    "药品召回":     PROMPT_RECALLS,
    "药品标签":     PROMPT_LABELS,
}


def _call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_OAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )
    return response.choices[0].message.content


def analyze_section(item: dict) -> dict:
    if item["error"]:
        return {"category": item["category"], "url": item["url"],
                "analysis": f"数据获取失败：{item['error']}"}
    prompt = PROMPT_MAP[item["category"]].format(text=item["text"])
    return {"category": item["category"], "url": item["url"],
            "analysis": _call_llm(prompt)}


def synthesize(analyses: list[dict]) -> str:
    combined = "\n\n".join(
        f"=== {a['category']} ===\n{a['analysis']}" for a in analyses
    )
    return _call_llm(PROMPT_SYNTHESIS.format(analyses=combined))


def summarize_all(items: list[dict]) -> tuple[list[dict], str]:
    analyses = []
    for item in items:
        print(f"    → 分析 {item['category']}...")
        analyses.append(analyze_section(item))
    print("    → 生成执行摘要...")
    return analyses, synthesize(analyses)
