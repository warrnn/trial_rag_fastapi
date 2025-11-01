from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
from contextlib import asynccontextmanager
from .config import ENV
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .database import knowledge_database
import json
from pathlib import Path

AI_ASSETS = {}

json_path = (
    Path(__file__).parent / "real_historical_data" / "mom_medic_historical_data.json"
)
with open(json_path, "r", encoding="utf-8") as f:
    user_history_data = json.load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Up AI Assets")

    embed_model = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
    AI_ASSETS["embedding_model"] = embed_model

    AI_ASSETS["knowledge_database"] = knowledge_database
    AI_ASSETS["knowledge_embeddings"] = embed_model.encode(
        knowledge_database, convert_to_tensor=True
    )

    user_history_docs = [
        (
            f"Pada {entry.get('timestamp')}: "
            + (
                f"Makan '{entry.get('meal_description')}'. "
                if entry.get("meal_description")
                else ""
            )
            + (
                f"Gula darah {entry.get('blood_glucose_mg_dl')} mg/dl. "
                if entry.get("blood_glucose_mg_dl")
                else ""
            )
            + (
                f"Suntik {entry.get('insulin_units')} unit insulin. "
                if entry.get("insulin_units")
                else ""
            )
            + (
                f"Kondisi: '{entry.get('condition_description')}'."
                if entry.get("condition_description")
                else ""
            )
        ).strip()
        for entry in user_history_data
    ]

    AI_ASSETS["user_history_docs"] = user_history_docs
    AI_ASSETS["user_history_embeddings"] = embed_model.encode(
        user_history_docs,
        convert_to_tensor=True,
    )

    AI_ASSETS["generator_model"] = pipeline(
        "text-generation",
        model=AutoModelForCausalLM.from_pretrained(
            ENV.GENERATOR_MODEL_NAME,
            device_map="cuda",
            torch_dtype="auto",
            trust_remote_code=False,
        ),
        tokenizer=AutoTokenizer.from_pretrained(ENV.GENERATOR_MODEL_NAME),
    )

    print("Startup complete")
    yield

    AI_ASSETS.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_embedded_knowledges():
    """Endpoint debug untuk melihat embeddings database pengetahuan."""
    if "knowledge_embeddings" in AI_ASSETS:
        return {"result": AI_ASSETS["knowledge_embeddings"].cpu().tolist()}
    return {"error": "Embeddings not loaded"}


@app.get("/generate/{question}")
def generate_answer_without_rag(question: str):
    """Endpoint dasar (non-RAG) yang rentan terhadap halusinasi."""

    torch.random.manual_seed(0)

    pipe = AI_ASSETS.get("generator_model")
    if pipe is None:
        return {"error": "Text generation pipeline not loaded."}, 500

    messages = [
        {
            "role": "system",
            "content": "You are an assistant who is ready to help and has knowledge about diabetes and helps users to provide recommendations and predictions about blood sugar.",
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "do_sample": False,
    }
    output = pipe(messages, **generation_args)
    return {"answer": output[0]["generated_text"]}


@app.get("/rag-without-history/{question}")
def retrieval_augmented_generation_without_user_historical_data(question: str):
    """Endpoint RAG yang hanya menggunakan Database Pengetahuan Umum."""

    torch.random.manual_seed(0)

    embed_model = AI_ASSETS.get("embedding_model")
    knowledge_db_embeddings = AI_ASSETS.get("knowledge_embeddings")
    pipe = AI_ASSETS.get("generator_model")
    knowledge_db = AI_ASSETS.get("knowledge_database")

    if (
        embed_model is None
        or knowledge_db_embeddings is None
        or pipe is None
        or knowledge_db is None
    ):
        return {"error": "AI Assets not loaded or are None."}, 500

    # Retrieval
    query_embedding = embed_model.encode(question, convert_to_tensor=True)

    similarities = util.cos_sim(query_embedding, knowledge_db_embeddings)

    top_k = min(3, len(knowledge_db))
    top_results = torch.topk(similarities, k=top_k)

    retrieved_contexts = []
    for score, index in zip(top_results.values[0], top_results.indices[0]):
        retrieved_contexts.append(
            {"fact": knowledge_db[index.item()], "score": score.item()}
        )

    # Augmentation
    context_string = " ".join([context["fact"] for context in retrieved_contexts])

    messages = [
        {
            "role": "system",
            "content": "You are a very cautious medical AI assistant. Answer user questions ONLY based on the given 'FACTUAL CONTEXT'. DO NOT use your internal knowledge. If the facts are insufficient to make a calculation, provide a medical alert based on them.",
        },
        {"role": "system", "content": f"KONTEKS FAKTA: {context_string}"},
        {"role": "user", "content": question},
    ]

    # Generation
    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "do_sample": False,
    }
    output = pipe(messages, **generation_args)

    return {
        "question": question,
        "retrieved_facts": retrieved_contexts,
        "answer": output[0]["generated_text"],
    }


@app.get("/rag-with-history/{question}")
def retrieval_augmented_generation_with_user_historical_data(question: str):
    """
    Endpoint RAG canggih: Menggabungkan Pengetahuan Umum + Riwayat Pasien Relevan.
    Menggunakan "threshold" untuk memfilter riwayat yang tidak relevan.
    """
    torch.random.manual_seed(0)

    embed_model = AI_ASSETS.get("embedding_model")
    pipe = AI_ASSETS.get("generator_model")

    knowledge_db = AI_ASSETS.get("knowledge_database")
    knowledge_db_embeddings = AI_ASSETS.get("knowledge_embeddings")

    user_history_docs = AI_ASSETS.get("user_history_docs")  # list of strings
    user_history_embeddings = AI_ASSETS.get("user_history_embeddings")

    if (
        embed_model is None
        or pipe is None
        or knowledge_db is None
        or knowledge_db_embeddings is None
        or user_history_docs is None
        or user_history_embeddings is None
    ):
        return {
            "error": "AI Assets (termasuk riwayat pasien) tidak dimuat dengan benar."
        }, 500

    query_embedding = embed_model.encode(question, convert_to_tensor=True)

    # Retrieval Fakta Umum
    sim_facts = util.cos_sim(query_embedding, knowledge_db_embeddings)
    top_k_facts = min(2, len(knowledge_db))  # Ambil 2 fakta umum teratas
    top_results_facts = torch.topk(sim_facts, k=top_k_facts)

    retrieved_facts = []
    for score, index in zip(top_results_facts.values[0], top_results_facts.indices[0]):
        retrieved_facts.append(
            {"fact": knowledge_db[index.item()], "score": score.item()}
        )
    context_string_facts = " ".join([context["fact"] for context in retrieved_facts])

    # Retrieval Riwayat Pasien
    HISTORY_RELEVANCE_THRESHOLD = 0.6  # 0.0 = tidak mirip, 1.0 = identik

    sim_history = util.cos_sim(query_embedding, user_history_embeddings)
    top_k_history = min(3, len(user_history_docs))  # Cek 3 riwayat teratas
    top_results_history = torch.topk(sim_history, k=top_k_history)

    retrieved_history = []

    top_history_score = top_results_history.values[0][0].item()

    if top_history_score >= HISTORY_RELEVANCE_THRESHOLD:
        print(
            f"DEBUG: Riwayat pasien RELEVAN (Skor: {top_history_score:.4f} >= {HISTORY_RELEVANCE_THRESHOLD}). Mengambil {top_k_history} riwayat."
        )
        for score, index in zip(
            top_results_history.values[0], top_results_history.indices[0]
        ):
            if score.item() >= HISTORY_RELEVANCE_THRESHOLD:
                retrieved_history.append(
                    {"fact": user_history_docs[index.item()], "score": score.item()}
                )
    else:
        print(
            f"DEBUG: Riwayat pasien TIDAK RELEVAN (Skor: {top_history_score:.4f} < {HISTORY_RELEVANCE_THRESHOLD}). Mengabaikan riwayat."
        )
        pass

    # Augmentation
    context_string_history = " ".join(
        [context["fact"] for context in retrieved_history]
    )
    if not context_string_history:
        context_string_history = (
            "Tidak ada riwayat pasien yang relevan dengan pertanyaan ini."
        )

    # Generation
    messages = [
        {
            "role": "system",
            "content": "You are a very cautious medical AI assistant. Answer user questions ONLY based on the given 'FACTUAL CONTEXT' and 'PATIENT HISTORY'. DO NOT use your internal knowledge. If the facts are insufficient to make a calculation, provide a medical alert based on them.",
        },
        {"role": "system", "content": f"KONTEKS FAKTA UMUM: {context_string_facts}"},
        {
            "role": "system",
            "content": f"KONTEKS RIWAYAT PASIEN: {context_string_history}",
        },
        {"role": "user", "content": question},
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "do_sample": False,
    }
    output = pipe(messages, **generation_args)
    return {
        "question": question,
        "retrieved_general_facts": retrieved_facts,
        "retrieved_patient_history": retrieved_history,
        "answer": output[0]["generated_text"],
    }
