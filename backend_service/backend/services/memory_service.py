import json
import math
import os
from datetime import UTC, datetime

from backend.core.openai_client import embed_text
from sqlalchemy import desc, select

from backend.services.db import SemanticMemory, get_session

try:
    from pinecone import Pinecone
except Exception:  # pragma: no cover
    Pinecone = None


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


def _utcnow() -> str:
    return datetime.now(UTC)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _pinecone_index():
    if not (PINECONE_API_KEY and PINECONE_INDEX_NAME and Pinecone):
        return None
    try:
        return Pinecone(api_key=PINECONE_API_KEY).Index(PINECONE_INDEX_NAME)
    except Exception:
        return None


def remember(user_id: str, memory_type: str, content: str, metadata: dict | None = None) -> None:
    metadata = metadata or {}
    embedding = embed_text(content)
    embedding_json = json.dumps(embedding)

    with get_session() as session:
        memory = SemanticMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            metadata_json=json.dumps(metadata),
            embedding_json=embedding_json,
            created_at=_utcnow(),
        )
        session.add(memory)
        session.commit()
        session.refresh(memory)
        memory_id = str(memory.id)

    index = _pinecone_index()
    if index is not None:
        try:
            index.upsert(
                vectors=[
                    {
                        "id": f"{user_id}:{memory_id}",
                        "values": embedding,
                        "metadata": {"user_id": user_id, "memory_type": memory_type, "content": content},
                    }
                ],
                namespace=user_id,
            )
        except Exception:
            pass


def search_memories(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    query_embedding = embed_text(query)
    index = _pinecone_index()
    if index is not None:
        try:
            result = index.query(vector=query_embedding, top_k=top_k, include_metadata=True, namespace=user_id)
            matches = []
            for match in result.get("matches", []):
                matches.append(
                    {
                        "content": match.get("metadata", {}).get("content", ""),
                        "memory_type": match.get("metadata", {}).get("memory_type", "memory"),
                        "score": match.get("score", 0),
                    }
                )
            if matches:
                return matches
        except Exception:
            pass

    with get_session() as session:
        rows = session.scalars(
            select(SemanticMemory)
            .where(SemanticMemory.user_id == user_id)
            .order_by(desc(SemanticMemory.id))
            .limit(200)
        ).all()

    scored = []
    for row in rows:
        embedding = json.loads(row.embedding_json)
        scored.append(
            {
                "memory_type": row.memory_type,
                "content": row.content,
                "metadata": json.loads(row.metadata_json),
                "score": _cosine_similarity(query_embedding, embedding),
                "created_at": row.created_at,
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def get_recent_memories(user_id: str, limit: int = 10) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(SemanticMemory)
            .where(SemanticMemory.user_id == user_id)
            .order_by(desc(SemanticMemory.id))
            .limit(limit)
        ).all()
    return [
        {
            "memory_type": row.memory_type,
            "content": row.content,
            "metadata": json.loads(row.metadata_json),
            "created_at": row.created_at,
        }
        for row in rows
    ]
