from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from .config import ENV

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)
    yield
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def convert_sentence_to_embedding():
    model = ml_models["embedding_model"]
    sentences = ["This is an example sentence", "Hello World"]
    embeddings = model.encode(sentences)
    return {"embeddings": embeddings.tolist()}
