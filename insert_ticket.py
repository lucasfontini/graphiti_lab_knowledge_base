
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

        ticket = """
        Ticket ID: 1004

        O serviço DIA apresentou perda de pacotes.
        O cliente informou instabilidade na conexão.
        O fornecedor responsável está investigando
        o incidente.
        """

        result = await graphiti.add_episode(
            name="Ticket INC1004",
            episode_body=ticket,
            source=EpisodeType.text,
            source_description="Ticket Zendesk",
            reference_time=datetime.now(timezone.utc),
            group_id="vendor-lab",
        )

        print("Novo ticket processado!")
        print(result)

    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
