from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
from contextlib import asynccontextmanager
from .config import ENV
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .database import knowledge_database

AI_ASSETS = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    AI_ASSETS["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
    AI_ASSETS["knowledge_embeddings"] = AI_ASSETS["embedding_model"].encode(
        knowledge_database
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

    yield

    AI_ASSETS.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_embedded_knowledges():
    return {"result": AI_ASSETS["knowledge_embeddings"].tolist()}


@app.get("/generate")
def generate_answer_without_rag():
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
            "content": "Saya barusan memakan pisang raja 2 buah, dalam 2 jam kedepan berapa gula darah saya jika pagi ini 150mg/dl?",
        },
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        # "temperature": 0.0,
        "do_sample": False,
    }

    output = pipe(messages, **generation_args)
    return {"answer": output[0]["generated_text"]}


@app.get("/rag/{question}")
def retrieval_augmented_generation(question: str):
    torch.random.manual_seed(0)

    embed_model = AI_ASSETS.get("embedding_model")
    knowledge_db_embeddings = AI_ASSETS.get("knowledge_embeddings")
    pipe = AI_ASSETS.get("generator_model")

    if embed_model is None or knowledge_db_embeddings is None or pipe is None:
        return {"error": "AI Assets not loaded or are None."}, 500

    query_embedding = embed_model.encode(question)

    similarities = util.cos_sim(query_embedding, knowledge_db_embeddings)

    top_k = min(3, len(knowledge_database))
    top_results = torch.topk(similarities, k=top_k)

    retrieved_contexts = []
    for score, index in zip(top_results.values[0], top_results.indices[0]):
        retrieved_contexts.append(
            {"fact": knowledge_database[index], "score": score.item()}
        )

    context_string = " ".join([context["fact"] for context in retrieved_contexts])

    messages = [
        {
            "role": "system",
            "content": "You are a very cautious medical AI assistant. Answer user questions ONLY based on the given 'FACTUAL CONTEXT'. DO NOT use your internal knowledge. If the facts are insufficient to make a calculation, provide a medical alert based on them.",
        },
        {
            "role": "system",
            "content": f"KONTEKS FAKTA: {context_string}",
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        # "temperature": 0.0,
        "do_sample": False,
    }

    output = pipe(messages, **generation_args)
    return {
        "question": question,
        "retrieved_facts": retrieved_contexts,
        "answer": output[0]["generated_text"],
    }
