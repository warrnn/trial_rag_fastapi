from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from .config import ENV
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load embedding model
    ml_models["embedding_model"] = SentenceTransformer(ENV.EMBEDDING_MODEL_NAME)

    # Load generator model (ONCE)
    model = AutoModelForCausalLM.from_pretrained(
        ENV.GENERATOR_MODEL_NAME,
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=False,
    )

    # Load tokenizer (ONCE)
    tokenizer = AutoTokenizer.from_pretrained(ENV.GENERATOR_MODEL_NAME)

    # Create the pipeline (ONCE) and store it in ml_models
    ml_models["text_gen_pipeline"] = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

    print("Models and pipeline loaded successfully.")  # Good for debugging
    yield

    # Clean up when server stops
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def convert_sentence_to_embedding():
    model = ml_models["embedding_model"]
    sentences = ["This is an example sentence", "Hello World"]
    embeddings = model.encode(sentences)
    return {"embeddings": embeddings.tolist()}


@app.get("/generate")
def generate_answer():
    torch.random.manual_seed(0)

    # Get the pipeline that was ALREADY loaded
    pipe = ml_models.get("text_gen_pipeline")

    if pipe is None:
        return {"error": "Text generation pipeline not loaded."}, 500

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {
            "role": "user",
            "content": "Can you provide ways to eat combinations of bananas and dragonfruits?",
        },
        {
            "role": "assistant",
            "content": "Sure! Here are some ways to eat bananas and dragonfruits together: 1. Banana and dragonfruit smoothie: Blend bananas and dragonfruits together with some milk and honey. 2. Banana and dragonfruit salad: Mix sliced bananas and dragonfruits together with some lemon juice and honey.",
        },
        {"role": "user", "content": "What about solving an 2x + 3 = 7 equation?"},
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "temperature": 0.0, 
        "do_sample": False,
    }

    output = pipe(messages, **generation_args)
    return {"answer": output[0]["generated_text"]}
