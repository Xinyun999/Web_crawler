import chromadb

# 模拟 Genentech 内部在研分子知识库
INTERNAL_MOLECULES = [
    {"id": "GNE-001",
     "text": "GNE-001 靶点 PD-L1，checkpoint inhibitor，适应症 NSCLC，Phase II。"
             "已知不良事件：免疫相关不良反应、结肠炎、肺炎、肝炎、内分泌异常。"},
    {"id": "GNE-002",
     "text": "GNE-002 靶点 HER2，抗体偶联药物(ADC)，适应症乳腺癌/胃癌，Phase III。"
             "已知不良事件：心脏毒性、周围神经病变、肺毒性、中性粒细胞减少。"},
    {"id": "GNE-003",
     "text": "GNE-003 靶点 VEGF，抗血管生成，适应症结直肠癌/肾癌，Phase II。"
             "已知不良事件：高血压、蛋白尿、出血、血栓栓塞事件。"},
    {"id": "GNE-004",
     "text": "GNE-004 靶点 BCL-2，venetoclax 类，适应症血液系统恶性肿瘤，Phase I。"
             "已知不良事件：肿瘤溶解综合征、中性粒细胞减少、感染、血小板减少。"},
    {"id": "GNE-005",
     "text": "GNE-005 靶点 KRAS G12C，适应症肺癌/结直肠癌，Phase II。"
             "已知不良事件：腹泻、恶心、肝毒性、QT 间期延长、肌肉骨骼疼痛。"},
]

_rag_instance = None


class MoleculeRAG:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("internal_molecules")
        self._load()

    def _load(self):
        self.collection.add(
            documents=[m["text"] for m in INTERNAL_MOLECULES],
            ids=[m["id"] for m in INTERNAL_MOLECULES],
        )

    def retrieve(self, query: str, n: int = 2) -> str:
        results = self.collection.query(query_texts=[query], n_results=n)
        docs = results["documents"][0] if results["documents"] else []
        if not docs:
            return "无相关内部分子数据"
        return "\n".join(f"- {d}" for d in docs)


def get_rag() -> MoleculeRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = MoleculeRAG()
    return _rag_instance
