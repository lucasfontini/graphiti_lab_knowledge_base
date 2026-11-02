
import os
from dotenv import load_dotenv

from graphiti_core.llm_client.groq_client import (
    GroqClient,
    LLMConfig,
)

from graphiti_core.embedder.gemini import (
    GeminiEmbedder,
    GeminiEmbedderConfig,
)

from graphiti_core.cross_encoder.gemini_reranker_client import (
    GeminiRerankerClient,
)

load_dotenv()

# API Keys
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY nao configurada")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nao configurada")


# LLM: Groq
llm_config = LLMConfig(
    api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
)

llm_client = GroqClient(config=llm_config)


# Embeddings: Gemini
embedder = GeminiEmbedder(
    config=GeminiEmbedderConfig(
        api_key=gemini_api_key,
        embedding_model="gemini-embedding-001",
        embedding_dim=3072,
    )
)


# Reranker: Gemini
reranker_config = LLMConfig(
    api_key=gemini_api_key,
    model="gemini-2.5-flash",
)

reranker = GeminiRerankerClient(
    config=reranker_config
)

print("Configuracao carregada:")
print(f"LLM: {type(llm_client).__name__}")
print(f"Embedder: {type(embedder).__name__}")
print(f"Reranker: {type(reranker).__name__}")
