from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from .config import ENV
from sentence_transformers import SentenceTransformer, util
from .database import (
    user_charateristics_database,
    hba1c_knowledge_database,
    knowledge_database,
)
import json
from pathlib import Path
from .helpers.format_helper import format_history_entry_to_string
from .services.generator_service import execute_text_generator, execute_hba1c_generator

ASSETS = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading AI assets...")

    # Retriever Assets
    ASSETS["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
    ASSETS["hba1c_knowledge_data"] = hba1c_knowledge_database
    # ASSETS["hba1c_knowledge_embeddings"] = ASSETS["embedding_model"].encode(
    #     hba1c_knowledge_database, convert_to_tensor=True
    # )
    ASSETS["knowledge_data"] = knowledge_database
    ASSETS["knowledge_embeddings"] = ASSETS["embedding_model"].encode(
        knowledge_database, convert_to_tensor=True
    )

    # User Data Assets
    ASSETS["user_charateristics_data"] = user_charateristics_database
    json_path = (
        Path(__file__).parent / "technical_data" / "mom_medic_historical_data.json"
    )
    with open(json_path, "r", encoding="utf-8") as f:
        user_history_data = json.load(f)
    ASSETS["user_history_data"] = user_history_data

    print("AI assets loaded.")

    yield

    ASSETS.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/rag/generate-text/{question}")
def exec_rag(question: str):
    user_biodata = ASSETS.get("user_charateristics_data")
    user_history = ASSETS.get("user_history_data")
    retriever = ASSETS.get("embedding_model")
    kb_embeddings = ASSETS.get("knowledge_embeddings")
    knowledge_db = ASSETS.get("knowledge_data")

    if (
        user_biodata is None
        or user_history is None
        or retriever is None
        or kb_embeddings is None
        or knowledge_db is None
    ):
        raise HTTPException(status_code=500, detail="Failed to load AI assets")

    # Fakta Pengetahuan Medis
    question_embedding = retriever.encode(question, convert_to_tensor=True)
    hits = util.semantic_search(question_embedding, kb_embeddings, top_k=3)
    retrieved_knowledge = " ".join([knowledge_db[hit["corpus_id"]] for hit in hits[0]])

    # Data Personal Log Terakhir
    NUM_RECENT_LOGS = 2
    recent_history_entries = user_history[-NUM_RECENT_LOGS:] if user_history else []

    history_docs_to_inject = [
        format_history_entry_to_string(entry) for entry in recent_history_entries
    ]
    context_string_history = " ".join(history_docs_to_inject)
    if not context_string_history:
        context_string_history = "Tidak ada data riwayat pasien."

    # Data Personal Biodata
    context_string_biodata = ". ".join(user_biodata).rstrip(".") + "."

    return {
        "question": question,
        "retrieved_user_biodata": context_string_biodata,
        "retrieved_patient_history": context_string_history,
        "retrieved_medical_facts": retrieved_knowledge,
        "answer": execute_text_generator(
            question=question,
            context_string_biodata=context_string_biodata,
            context_string_history=context_string_history,
            retrieved_knowledge=retrieved_knowledge,
        ),
    }


@app.get("/rag/generate-hba1c")
def exec_hba1c():
    user_biodata = ASSETS.get("user_charateristics_data")
    user_history = ASSETS.get("user_history_data")
    hba1c_knowledge_db = ASSETS.get("hba1c_knowledge_data")

    if user_biodata is None or user_history is None or hba1c_knowledge_db is None:
        raise HTTPException(status_code=500, detail="Failed to load AI assets")

    # Fakta Pengetahuan hba1c
    retrieved_hb1ac_knowledge = " ".join(hba1c_knowledge_db)

    # Data Personal Log Terakhir
    NUM_RECENT_LOGS = 2
    recent_history_entries = user_history[-NUM_RECENT_LOGS:] if user_history else []

    history_docs_to_inject = [
        format_history_entry_to_string(entry) for entry in recent_history_entries
    ]
    context_string_history = " ".join(history_docs_to_inject)
    if not context_string_history:
        context_string_history = "Tidak ada data riwayat pasien."

    # Data Personal Biodata
    context_string_biodata = ". ".join(user_biodata).rstrip(".") + "."

    return {
        "answer": execute_hba1c_generator(
            context_string_biodata=context_string_biodata,
            context_string_history=context_string_history,
            retrieved_hba1c_knowledge=retrieved_hb1ac_knowledge,
        ),
    }
