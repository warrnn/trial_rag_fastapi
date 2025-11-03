from fastapi import HTTPException
from google import genai
from ..config import ENV


def execute_text_generator(
    model=ENV.GEMINI_GENERATOR_MODEL,
    question=None,
    context_string_biodata=None,
    context_string_history=None,
    retrieved_knowledge=None,
):
    if question is None:
        return HTTPException(status_code=400, detail="No question provided")

    try:
        client = genai.Client(api_key=ENV.GEMINI_API_KEY)

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

        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
        )

        return response.text
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate answer")
