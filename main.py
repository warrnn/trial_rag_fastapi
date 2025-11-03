from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from .config import ENV
from sentence_transformers import SentenceTransformer, util
from google import genai
from .database import user_charateristics_database, knowledge_database
import json
from pathlib import Path
from .helpers.format_helper import format_history_entry_to_string

ASSETS = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ASSETS["user_charateristics_data"] = user_charateristics_database
    ASSETS["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
    ASSETS["knowledge_data"] = knowledge_database
    ASSETS["knowledge_embeddings"] = ASSETS["embedding_model"].encode(
        knowledge_database, convert_to_tensor=True
    )

    json_path = (
        Path(__file__).parent
        / "real_historical_data"
        / "mom_medic_historical_data.json"
    )
    with open(json_path, "r", encoding="utf-8") as f:
        user_history_data = json.load(f)
    ASSETS["user_history_data"] = user_history_data

    yield

    ASSETS.clear()


app = FastAPI(lifespan=lifespan)


def generate_gemini_answer(model=ENV.GEMINI_GENERATOR_MODEL, question=None):
    if question is None:
        return HTTPException(status_code=400, detail="No question provided")

    try:
        client = genai.Client(api_key=ENV.GEMINI_API_KEY)

        response = client.models.generate_content(
            model=model,
            contents=question,
        )

        return {
            # "question": question,
            "answer": response.text
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate answer")


@app.get("/{question}")
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

    system_prompt = f"""Anda adalah asisten diabetes personal yang ramah dan berpengetahuan.
                        Tugas Anda adalah menjawab pertanyaan pengguna dan usahakan memberikan prediksi gula darah (mg/dl).

                        Gunakan informasi di bawah ini untuk merumuskan jawaban Anda:
                        
                        DATA DIRI PASIEN:
                        {context_string_biodata}

                        LOG PASIEN TERAKHIR (Gunakan untuk personalisasi dan melihat kondisi terbaru):
                        {context_string_history}
                        
                        FAKTA MEDIS (Gunakan sebagai sumber kebenaran untuk perhitungan dan saran):
                        {retrieved_knowledge}

                        CARA MENJAWAB:
                        - Sapa pasien dengan namanya (jika ada di DATA DIRI).
                        - Jawab pertanyaan pengguna secara langsung.
                        - Jika pengguna meminta prediksi gula darah (misal setelah makan 'pisang'), gunakan 'FAKTA MEDIS' untuk membuat estimasi perhitungan (misal: pisang 30g karbo, 15g karbo naik 30-50mg/dl, dll).
                        - Gunakan 'LOG PASIEN TERAKHIR' untuk melihat kondisi terbaru (misal: "Saya lihat log terakhir Anda menunjukkan gula darah 192 mg/dl dengan kondisi pusing, jadi...").
                        - Berikan rekomendasi singkat dan yang relevan.
                        - SELALU akhiri jawaban Anda dengan peringatan medis bahwa ini adalah estimasi dan bukan pengganti nasihat dokter.
                        """

    full_prompt = system_prompt + f"\n\nPERTANYAAN PENGGUNA:\n{question}"

    return {
        "question": question,
        "retrieved_user_biodata": user_biodata,
        "retrieved_patient_history": recent_history_entries,
        "retrieved_medical_facts": retrieved_knowledge,
        "answer": generate_gemini_answer(question=full_prompt),
    }
