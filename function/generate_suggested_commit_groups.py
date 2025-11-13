from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
import uuid
from scipy.cluster.hierarchy import linkage, fcluster

_model: SentenceTransformer = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_atomic_diffs(atomic_diffs: List[Dict[str, Any]]) -> np.ndarray:
    model = get_model()
    texts = [
        f"file: {d['file']}\n"
        f"old:\n" + "\n".join(d.get("old_lines", [])) + "\n"
        f"new:\n" + "\n".join(d.get("new_lines", []))
        for d in atomic_diffs
    ]
    embeddings = model.encode(texts, show_progress_bar=False)
    return np.array(embeddings)

def generate_suggested_commit_groups_agglomerative(
    atomic_diffs: List[Dict[str, Any]], similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    使用层次聚类（agglomerative clustering）生成 suggested commit groups
    similarity_threshold: cosine similarity threshold (0~1)
    """
    if not atomic_diffs:
        return []

    embeddings = embed_atomic_diffs(atomic_diffs)
    
    # 层次聚类 linkage，使用 cosine 距离
    # 注意 scipy 的 linkage 接收距离矩阵或特征矩阵
    Z = linkage(embeddings, method='average', metric='cosine')

    # fcluster 生成簇，距离阈值 = 1 - similarity_threshold
    labels = fcluster(Z, t=1 - similarity_threshold, criterion='distance')
    
    # 构造分组
    groups_dict = {}
    for idx, label in enumerate(labels):
        groups_dict.setdefault(label, []).append(atomic_diffs[idx])
    
    groups = []
    for label, diffs in groups_dict.items():
        groups.append({
            "id": str(uuid.uuid4()),
            "name": f"Suggested Group {label}",
            "diffs": diffs
        })
    
    return groups