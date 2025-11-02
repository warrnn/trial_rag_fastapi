from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from .config import ENV
from sentence_transformers import SentenceTransformer
from google import genai
from .database import knowledge_database
import json
from pathlib import Path
from .helpers.format_helper import format_history_entry_to_string

ASSETS = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ASSETS["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
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

        return {"question": question, "answer": response.text}
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail="Failed to generate answer")


@app.get("/{question}")
def exec_rag(question: str):
    user_history = ASSETS.get("user_history_data")

    if user_history is None:
        return HTTPException(status_code=500, detail="Failed to generate answer")

    NUM_RECENT_LOGS = 2
    recent_history_entries = user_history[-NUM_RECENT_LOGS:] if user_history else []

    history_docs_to_inject = [
        format_history_entry_to_string(entry) for entry in recent_history_entries
    ]
    context_string_history = " ".join(history_docs_to_inject)
    if not context_string_history:
        context_string_history = "Tidak ada data riwayat pasien."

    system_prompt = f"""Anda adalah asisten diabetes personal yang ramah dan berpengetahuan.
                    Tugas Anda adalah menjawab pertanyaan pengguna dan usahakan memberikan prediksi gula darah (mg/dl).

                    Gunakan informasi di bawah ini untuk merumuskan jawaban Anda:
                    LOG PASIEN TERAKHIR (Gunakan untuk personalisasi dan melihat kondisi terbaru):
                    {context_string_history}

                    CARA MENJAWAB:
                    - Jawab pertanyaan pengguna secara langsung.
                    - Jika pengguna meminta prediksi gula darah (misal setelah makan 'pisang'), gunakan 'FAKTA MEDIS' untuk membuat estimasi perhitungan (misal: pisang 30g karbo, 15g karbo naik 30-50mg/dl, dll).
                    - Gunakan 'LOG PASIEN TERAKHIR' untuk melihat kondisi terbaru (misal: "Saya lihat log terakhir Anda menunjukkan gula darah 192 mg/dl dengan kondisi pusing, jadi...").
                    - Berikan rekomendasi singkat dan yang relevan.
                    - SELALU akhiri jawaban Anda dengan peringatan medis bahwa ini adalah estimasi dan bukan pengganti nasihat dokter.
                    """

    full_prompt = system_prompt + f"\n\nPERTANYAAN PENGGUNA:\n{question}"

    return {
        "question": question,
        "retrieved_patient_history": recent_history_entries,
        "answer": generate_gemini_answer(question=full_prompt),
    }
