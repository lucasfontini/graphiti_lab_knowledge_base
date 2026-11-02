
import asyncio
import os

from datetime import datetime, timezone
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from config import llm_client, embedder, reranker


async def main():

    load_dotenv()

    graphiti = Graphiti(
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD"),
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
    )

    try:

        texto = """
        O fornecedor Lumen é responsável pelo circuito ABC123.
        O circuito atende o cliente Acme e está localizado em Curitiba.
        """

        print("Inserindo episodio...")

        result = await graphiti.add_episode(
            name="Cadastro inicial do circuito ABC123",
            episode_body=texto,
            source=EpisodeType.text,
            source_description="Cadastro de circuito",
            reference_time=datetime.now(timezone.utc),
        )

        print("Episodio inserido!")
        print("Resultado:", result)

    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
