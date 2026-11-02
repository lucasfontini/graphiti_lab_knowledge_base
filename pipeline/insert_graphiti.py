
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from graphiti_core.nodes import EpisodeType

from config import llm_client, embedder, reranker




'''
from graphiti_core.nodes import EpisodeType

EpisodeType.message: mensagens e conversas.
EpisodeType.json: dados estruturados.
EpisodeType.text: textos e documentos.


'''



BASE_DIR = Path(__file__).resolve().parent


async def main():

    # 1. Carregar ticket e conhecimento
    with open(BASE_DIR / "conhecimento_extraido.json", encoding="utf-8") as f:
        ticket = json.load(f)

    with open(BASE_DIR / "conhecimento_validado.json", encoding="utf-8") as f:
        conhecimentos = json.load(f)

    # 2. Conectar ao Neo4j
    graph_driver = Neo4jDriver(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="neo4j"
    )

    # 3. Inicializar Graphiti
    graphiti = Graphiti(
        graph_driver=graph_driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
        max_coroutines=1
    )

    try:
        # 4. Preparar o conteúdo do episódio
        conteudo = f"""
        Ticket: {ticket['ticket_id']}
        Cliente: {ticket['customer']}
        Circuito: {ticket['circuit_id']}
        Provedor: {ticket['provider']}

        Conhecimentos extraídos:
        """

        for item in conhecimentos:
            conteudo += f"""
            Tipo: {item['type']}
            Classificação: {item['classification']}
            Conteúdo: {item['content']}
            Origem: {item['source']}
            """

        # 5. Inserir episódio
        resultado = await graphiti.add_episode(
            name=f"Zendesk {ticket['ticket_id']}",
            episode_body=conteudo,
            source_description="Ticket encerrado do Zendesk com conhecimento extraído",
            source=EpisodeType.json,
            reference_time=datetime.now(timezone.utc),
            group_id="noc"
        )

        print("Episódio inserido!")
        print("UUID:", resultado.episode.uuid)

    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
