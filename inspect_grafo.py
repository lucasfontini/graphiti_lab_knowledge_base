
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


def inspect_graph(tx):

    print("\n========== NOS EXISTENTES ==========\n")

    query_nodes = """
    MATCH (n)
    RETURN labels(n) AS labels,
           properties(n) AS properties
    ORDER BY labels
    """

    nodes = list(tx.run(query_nodes))

    for node in nodes:
        print(f"Tipo: {node['labels']}")
        print(f"Dados: {clean_properties(node['properties'])}")
        print("-" * 50)

    print("\n========== RELACIONAMENTOS ==========\n")

    query_relationships = """
    MATCH (a)-[r]->(b)
    RETURN labels(a) AS origem,
           properties(a) AS dados_origem,
           type(r) AS relacionamento,
           properties(r) AS dados_relacionamento,
           labels(b) AS destino,
           properties(b) AS dados_destino
    """

    relationships = list(tx.run(query_relationships))

    for rel in relationships:
        print(f"ORIGEM: {rel['origem']} {rel['dados_origem']}")
        print(f"RELACAO: {rel['relacionamento']}")
        print(f"DESTINO: {rel['destino']} {rel['dados_destino']}")
        print("-" * 70)

    print("\n========== TICKETS E SERVICOS ==========\n")

    query_tickets = """
    MATCH (t:Ticket)
    OPTIONAL MATCH (t)-[r]-(s:Service)
    RETURN properties(t) AS ticket,
           type(r) AS relacionamento,
           properties(s) AS servico
    ORDER BY ticket.id
    """

    tickets = list(tx.run(query_tickets))

    for item in tickets:
        print(f"TICKET: {item['ticket']}")
        print(f"RELACAO: {item['relacionamento']}")
        print(f"SERVICO: {item['servico']}")
        print("-" * 50)

    print(f"\nTotal de nos: {len(nodes)}")
    print(f"Total de relacionamentos: {len(relationships)}")

def clean_properties(properties):

    ignored = [
        "embedding",
        "name_embedding",
        "fact_embedding",
    ]

    return {
        key: value
        for key, value in properties.items()
        if not any(item in key.lower() for item in ignored)
    }

def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USER, PASSWORD)
    )

    try:
        driver.verify_connectivity()
        print("Conectado ao Neo4j!")

        with driver.session() as session:
            session.execute_read(inspect_graph)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
