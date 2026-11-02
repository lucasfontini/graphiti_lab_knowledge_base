
import asyncio
import os

from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.driver.neo4j_driver import Neo4jDriver

from config import llm_client, embedder, reranker


# ==========================================
# CONFIGURACOES
# ==========================================

load_dotenv()

DATABASE = "neo4j"
GROUP_ID = "vendor-lab-demo"

DELAY_SECONDS = 5

# ==========================================
# EPISODIOS DO LABORATORIO
# ==========================================

episodes = [

    # CADASTRO DE CIRCUITOS - NETBOX

    {
        "name": "Cadastro CIR-1001",
        "source": "NetBox",
        "body": """
        O circuito CIR-1001 pertence ao cliente Acme Telecom.
        O fornecedor responsavel e Lumen.
        A tecnologia e DIA (Dedicated Internet Access).
        A velocidade contratada e 500 Mbps.
        O circuito esta localizado em Curitiba, Parana.
        """
    },

    {
        "name": "Cadastro CIR-1002",
        "source": "NetBox",
        "body": """
        O circuito CIR-1002 pertence ao cliente Global Bank.
        O fornecedor responsavel e Vodafone.
        A tecnologia e MPLS.
        A velocidade contratada e 1 Gbps.
        O circuito esta localizado em Sao Paulo.
        """
    },

    {
        "name": "Cadastro CIR-1003",
        "source": "NetBox",
        "body": """
        O circuito CIR-1003 pertence ao cliente Tech Solutions.
        O fornecedor responsavel e Claro.
        A tecnologia e DIA.
        A velocidade contratada e 300 Mbps.
        O circuito esta localizado em Porto Alegre.
        """
    },

    {
        "name": "Cadastro CIR-1004",
        "source": "NetBox",
        "body": """
        O circuito CIR-1004 pertence ao cliente Acme Telecom.
        O fornecedor responsavel e Lumen.
        A tecnologia e Ethernet.
        A velocidade contratada e 1 Gbps.
        O circuito esta localizado em Curitiba, Parana.
        """
    },

    {
        "name": "Cadastro CIR-1005",
        "source": "NetBox",
        "body": """
        O circuito CIR-1005 pertence ao cliente Global Bank.
        O fornecedor responsavel e Vodafone.
        A tecnologia e DIA.
        A velocidade contratada e 200 Mbps.
        O circuito esta localizado no Rio de Janeiro.
        """
    },

    # TICKETS - ZENDESK

    {
        "name": "Ticket INC-1001",
        "source": "Zendesk",
        "body": """
        Ticket INC-1001.
        Cliente Acme Telecom.
        Circuito afetado CIR-1001.
        Problema: Packet Loss.
        O cliente reportou perda de pacotes de aproximadamente 15%.
        O fornecedor Lumen iniciou a investigacao.
        Status: Closed.
        """
    },

    {
        "name": "Ticket INC-1002",
        "source": "Zendesk",
        "body": """
        Ticket INC-1002.
        Cliente Acme Telecom.
        Circuito afetado CIR-1001.
        Problema: High Latency.
        A latencia chegou a 250 ms.
        O fornecedor Lumen realizou testes no circuito.
        Status: Closed.
        """
    },

    {
        "name": "Ticket INC-1003",
        "source": "Zendesk",
        "body": """
        Ticket INC-1003.
        Cliente Global Bank.
        Circuito afetado CIR-1002.
        Problema: Link Down.
        O circuito ficou indisponivel.
        O fornecedor Vodafone esta investigando.
        Status: Open.
        """
    },

    {
        "name": "Ticket INC-1004",
        "source": "Zendesk",
        "body": """
        Ticket INC-1004.
        Cliente Tech Solutions.
        Circuito afetado CIR-1003.
        Problema: Packet Loss.
        Foram identificadas perdas intermitentes.
        O fornecedor Claro esta analisando o incidente.
        Status: Open.
        """
    },

    {
        "name": "Ticket INC-1005",
        "source": "Zendesk",
        "body": """
        Ticket INC-1005.
        Cliente Acme Telecom.
        Circuito afetado CIR-1004.
        Problema: High Latency.
        O cliente reportou lentidao.
        A Lumen iniciou testes.
        Status: Open.
        """
    },

    {
        "name": "Ticket INC-1006",
        "source": "Zendesk",
        "body": """
        Ticket INC-1006.
        Cliente Global Bank.
        Circuito afetado CIR-1005.
        Problema: Packet Loss.
        O cliente identificou perda de pacotes.
        A Vodafone esta investigando.
        Status: Closed.
        """
    },

    {
        "name": "Ticket INC-1007",
        "source": "Zendesk",
        "body": """
        Ticket INC-1007.
        Cliente Acme Telecom.
        Circuito afetado CIR-1001.
        Problema: Intermittent Connectivity.
        O cliente informou novas oscilacoes.
        A Lumen esta acompanhando o caso.
        Status: Open.
        """
    },

    {
        "name": "Ticket INC-1008",
        "source": "Zendesk",
        "body": """
        Ticket INC-1008.
        Cliente Tech Solutions.
        Circuito afetado CIR-1003.
        Problema: High Latency.
        A latencia aumentou durante o horario de pico.
        O fornecedor Claro esta investigando.
        Status: Closed.
        """
    },

    # EMAILS DOS FORNECEDORES

    {
        "name": "Email Lumen - Manutencao",
        "source": "Email",
        "body": """
        A Lumen informou uma manutencao na regiao de Curitiba.
        A manutencao pode afetar o circuito CIR-1001.
        A janela prevista e das 02:00 as 04:00 UTC.
        O fornecedor espera normalizar o servico apos a atividade.
        """
    },

    {
        "name": "Email Vodafone - Incidente",
        "source": "Email",
        "body": """
        A Vodafone confirmou uma falha de equipamento que pode afetar
        o circuito CIR-1002 do cliente Global Bank.
        A equipe de engenharia esta trabalhando na restauracao.
        Ainda nao existe previsao definitiva de normalizacao.
        """
    },

    {
        "name": "Email Claro - RCA",
        "source": "Email",
        "body": """
        A Claro enviou uma atualizacao sobre o circuito CIR-1003.
        Foi identificada uma falha de transmissao.
        A causa esta relacionada a uma degradacao de equipamento.
        A Claro informou que esta preparando o RCA.
        """
    },
]


# ==========================================
# INGESTAO
# ==========================================

async def main():

    graph_driver = Neo4jDriver(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=DATABASE,
    )

    graphiti = Graphiti(
        graph_driver=graph_driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
        max_coroutines=1,
    )

    try:

        print("\nInicializando Graphiti...")
        print(f"Database: {DATABASE}")
        print(f"Group ID: {GROUP_ID}")

        await graphiti.build_indices_and_constraints()

        start_time = datetime.now(timezone.utc)

        inserted = 0
        skipped = 0

        for index, episode in enumerate(episodes):

            # Verifica se ja existe episodio com mesmo nome e grupo
            existing = await graph_driver.execute_query(
                """
                MATCH (e:Episodic {
                    name: $name,
                    group_id: $group_id
                })
                RETURN count(e) AS total
                """,
                name=episode["name"],
                group_id=GROUP_ID,
            )

            records = existing.records
            if records and records[0]["total"] > 0:

                print(
                    f"[{index + 1}/{len(episodes)}] "
                    f"Ja existe: {episode['name']}"
                )

                skipped += 1
                continue

            print(
                f"\n[{index + 1}/{len(episodes)}] "
                f"Inserindo: {episode['name']}"
            )

            result = await graphiti.add_episode(
                name=episode["name"],
                episode_body=episode["body"],
                source=EpisodeType.text,
                source_description=episode["source"],
                reference_time=start_time + timedelta(minutes=index),
                group_id=GROUP_ID,
            )

            print(f"UUID: {result.episode.uuid}")
            print("Inserido com sucesso!")

            inserted += 1

            if index < len(episodes) - 1:
                await asyncio.sleep(DELAY_SECONDS)

        print("\n" + "=" * 50)
        print("SEED FINALIZADO!")
        print(f"Total planejado: {len(episodes)}")
        print(f"Novos episodios: {inserted}")
        print(f"Ja existentes: {skipped}")
        print(f"Database: {DATABASE}")
        print("=" * 50)

    finally:

        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
