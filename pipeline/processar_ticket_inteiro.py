import argparse
import asyncio
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from config import llm_client, embedder, reranker
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from graphiti_core.llm_client.client import Message
from graphiti_core.nodes import EpisodeType


# Este arquivo deve ficar em graphiti_lab/pipeline/processar_ticket.py
PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PIPELINE_DIR.parent
GROUP_ID = "noc"

BASE_FILE = PIPELINE_DIR / "base_conhecimento.json"
INCIDENTS_FILE = PIPELINE_DIR / "incidentes.json"
OUTPUT_DIR = PIPELINE_DIR / "processed"

VALID_TYPES = {
    "symptom",
    "technical_evidence",
    "root_cause",
    "action",
    "resolution",
    "operational_learning",
}
VALID_CLASSIFICATIONS = {"fact", "inference", "hypothesis"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def load_json(path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json_atomic(path, data):
    """Grava em arquivo temporário e substitui o destino ao terminar."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    os.replace(temporary, path)


def normalize_text(value):
    value = (value or "").lower().strip()
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        char for char in value
        if unicodedata.category(char) != "Mn"
    )
    value = re.sub(r"[^\w\s]", "", value)
    return re.sub(r"\s+", " ", value)


def knowledge_key(item):
    """Chave determinística: mesma entidade, tipo e texto normalizado."""
    return (
        item.get("circuit_id", ""),
        item.get("provider", ""),
        item.get("type", ""),
        normalize_text(item.get("content", "")),
    )


def parse_reference_time(ticket):
    """Usa o fechamento; se ausente, usa o comentário mais recente."""
    value = ticket.get("closed_at")

    if not value and ticket.get("comments"):
        value = max(
            comment["timestamp"]
            for comment in ticket["comments"]
            if comment.get("timestamp")
        )

    if not value:
        return datetime.now(timezone.utc)

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_context(ticket):
    comments = sorted(
        ticket.get("comments", []),
        key=lambda item: item.get("timestamp", "")
    )

    lines = [
        f"TICKET: {ticket['ticket_id']}",
        f"ASSUNTO: {ticket.get('subject', '')}",
        f"STATUS: {ticket.get('status', '')}",
        f"CLIENTE: {ticket.get('customer', {}).get('name', '')}",
        f"CIRCUITO: {ticket.get('service', {}).get('circuit_id', '')}",
        f"SERVIÇO: {ticket.get('service', {}).get('type', '')}",
        f"PROVEDOR: {ticket.get('provider', {}).get('name', '')}",
        "",
        "HISTÓRICO DE COMENTÁRIOS:",
    ]

    for comment in comments:
        lines.extend([
            "",
            f"ID DO COMENTÁRIO: {comment.get('id')}",
            f"[{comment.get('timestamp', '')}]",
            f"Autor: {comment.get('author', '')}",
            f"Origem: {comment.get('source', '')}",
            f"Mensagem: {comment.get('message', '')}",
        ])

    return "\n".join(lines)


def build_prompt(context):
    return f"""
Você é um analista especialista em troubleshooting de redes
e telecomunicações.

Analise o histórico completo do ticket e extraia conhecimentos
relevantes para uma base de conhecimento do NOC.

REGRAS:
1. Não invente informações.
2. Diferencie fatos confirmados, inferências e hipóteses.
3. Preserve evidências técnicas e a origem de cada informação.
4. Não transforme suspeitas em fatos.
5. Não generalize conclusões de um único incidente.
6. Ignore comentários administrativos sem valor técnico.
7. Cada conhecimento deve representar uma única informação.
8. source_comment_id DEVE ser o ID numérico do comentário original,
   e NÃO a data/hora. Se não houver comentário específico, use null.
9. Use o autor do comentário como source.
10. Responda exclusivamente com JSON válido.

CLASSIFICAÇÕES:
- fact: informação explicitamente relatada/confirmada.
- inference: conclusão derivada das evidências.
- hypothesis: possibilidade ainda não confirmada.

TIPOS:
- symptom
- technical_evidence
- root_cause
- action
- resolution
- operational_learning

CONFIANÇA:
- high
- medium
- low

ESTRUTURA:
{{
  "ticket_id": "",
  "customer": "",
  "circuit_id": "",
  "provider": "",
  "knowledge": [
    {{
      "content": "",
      "type": "",
      "classification": "",
      "confidence": "",
      "source": "",
      "source_comment_id": null
    }}
  ]
}}

HISTÓRICO:
{context}
"""


async def extract_knowledge(context):
    print("Enviando histórico para o Groq...")

    response = await llm_client.generate_response(
        messages=[
            Message(role="user", content=build_prompt(context))
        ]
    )

    if isinstance(response, str):
        response = json.loads(response)

    if not isinstance(response, dict):
        raise ValueError("A resposta do LLM não é um objeto JSON.")

    return response


def normalize_comment_references(knowledge, ticket):
    """Corrige timestamp no campo source_comment_id usando o ID real do ticket."""
    by_timestamp = {
        comment.get("timestamp"): comment.get("id")
        for comment in ticket.get("comments", [])
        if comment.get("timestamp") and comment.get("id") is not None
    }
    valid_ids = {
        str(comment.get("id"))
        for comment in ticket.get("comments", [])
        if comment.get("id") is not None
    }

    for item in knowledge:
        ref = item.get("source_comment_id")

        if ref is None:
            continue

        ref_string = str(ref)

        if ref_string in by_timestamp:
            item["source_comment_id"] = by_timestamp[ref_string]
        elif ref_string in valid_ids:
            item["source_comment_id"] = int(ref_string)
        else:
            print(
                "Aviso: source_comment_id não corresponde a um comentário; "
                "definindo como null."
            )
            item["source_comment_id"] = None

    return knowledge


def validate_knowledge(extracted, ticket):
    if extracted.get("ticket_id") != ticket.get("ticket_id"):
        raise ValueError("O ticket_id retornado pelo LLM não corresponde ao ticket de entrada.")

    knowledge = extracted.get("knowledge")
    if not isinstance(knowledge, list):
        raise ValueError("A resposta do LLM não contém uma lista 'knowledge'.")

    knowledge = normalize_comment_references(knowledge, ticket)
    valid = []

    for index, item in enumerate(knowledge, start=1):
        errors = []

        if not isinstance(item, dict):
            print(f"Conhecimento {index} rejeitado: item não é objeto.")
            continue

        if not item.get("content"):
            errors.append("content vazio")
        if item.get("type") not in VALID_TYPES:
            errors.append("type inválido")
        if item.get("classification") not in VALID_CLASSIFICATIONS:
            errors.append("classification inválida")
        if item.get("confidence") not in VALID_CONFIDENCE:
            errors.append("confidence inválida")
        if not item.get("source"):
            errors.append("source ausente")

        if errors:
            print(f"Conhecimento {index} rejeitado: {', '.join(errors)}")
            continue

        enriched = dict(item)
        enriched["circuit_id"] = ticket["service"]["circuit_id"]
        enriched["provider"] = ticket["provider"]["name"]
        enriched["source_ticket"] = ticket["ticket_id"]
        valid.append(enriched)

    if not valid:
        raise ValueError("Nenhum conhecimento válido foi extraído.")

    return valid


def merge_knowledge(existing_base, validated, ticket_id):
    """Deduplica fatos e preserva todos os tickets que os reportaram."""
    base = list(existing_base)
    index = {knowledge_key(item): item for item in base}

    inserted = 0
    updated = 0

    for item in validated:
        key = knowledge_key(item)

        if key in index:
            existing = index[key]

            source_tickets = existing.get("source_tickets")
            if source_tickets is None:
                old_ticket = existing.pop("source_ticket", None)
                source_tickets = [old_ticket] if old_ticket else []
                existing["source_tickets"] = source_tickets

            if ticket_id not in source_tickets:
                source_tickets.append(ticket_id)

            existing["occurrences"] = len(source_tickets)
            updated += 1
        else:
            new_item = dict(item)
            new_item["source_tickets"] = [ticket_id]
            new_item["occurrences"] = 1
            base.append(new_item)
            index[key] = new_item
            inserted += 1

    return base, inserted, updated


def build_episode_body(ticket, validated):
    payload = {
        "ticket": ticket,
        "extracted_knowledge": validated,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def insert_graphiti_episode(ticket, validated):
    graph_driver = Neo4jDriver(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="neo4j",
    )

    graphiti = Graphiti(
        graph_driver=graph_driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
        max_coroutines=1,
    )

    try:
        result = await graphiti.add_episode(
            name=f"Zendesk {ticket['ticket_id']}",
            episode_body=build_episode_body(ticket, validated),
            source_description="Ticket encerrado do Zendesk e conhecimentos extraídos pela pipeline NOC",
            source=EpisodeType.json,
            reference_time=parse_reference_time(ticket),
            group_id=GROUP_ID,
        )
        return result.episode.uuid
    finally:
        await graphiti.close()


async def process_ticket(ticket_path):
    ticket_path = Path(ticket_path)
    if not ticket_path.is_absolute():
        ticket_path = (Path.cwd() / ticket_path).resolve()

    if not ticket_path.exists():
        raise FileNotFoundError(f"Ticket não encontrado: {ticket_path}")

    ticket = load_json(ticket_path)
    ticket_id = ticket["ticket_id"]

    if ticket.get("status", "").lower() != "closed":
        raise ValueError(
            f"O ticket {ticket_id} está com status '{ticket.get('status')}'. "
            "Esta pipeline só processa tickets fechados."
        )

    incidents = load_json(INCIDENTS_FILE, default=[])
    if any(item.get("ticket_id") == ticket_id for item in incidents):
        print(f"Ticket {ticket_id} já consta como processado. Encerrando sem alterações.")
        return

    print(f"\n=== Processando {ticket_id} ===")

    # 1. Preparar histórico
    context = build_context(ticket)
    output_dir = OUTPUT_DIR / ticket_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "contexto_ticket.txt").write_text(context, encoding="utf-8")
    print("1/6 Histórico preparado.")

    # 2. Extrair com Groq
    extracted = await extract_knowledge(context)
    save_json_atomic(output_dir / "conhecimento_extraido.json", extracted)
    print(f"2/6 Extração concluída: {len(extracted.get('knowledge', []))} itens.")

    # 3. Validar
    validated = validate_knowledge(extracted, ticket)
    save_json_atomic(output_dir / "conhecimento_validado.json", validated)
    print(f"3/6 Validação concluída: {len(validated)} itens válidos.")

    # 4. Calcular deduplicação, sem persistir ainda
    current_base = load_json(BASE_FILE, default=[])
    merged_base, inserted, updated = merge_knowledge(
        current_base, validated, ticket_id
    )
    print(f"4/6 Deduplicação: {inserted} novos, {updated} conhecimentos atualizados.")

    # 5. Inserir o episódio. O ticket é um evento novo mesmo que alguns fatos
    # já existam na base consolidada.
    print("5/6 Inserindo episódio no Graphiti...")
    episode_uuid = await insert_graphiti_episode(ticket, validated)
    print(f"Episódio inserido no Graphiti: {episode_uuid}")

    # 6. Persistir os arquivos locais somente após sucesso no Graphiti
    incidents.append({
        "ticket_id": ticket_id,
        "circuit_id": ticket["service"]["circuit_id"],
        "provider": ticket["provider"]["name"],
        "status": "processed",
        "group_id": GROUP_ID,
        "graphiti_episode_uuid": episode_uuid,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    })

    save_json_atomic(BASE_FILE, merged_base)
    save_json_atomic(INCIDENTS_FILE, incidents)

    save_json_atomic(output_dir / "resultado.json", {
        "ticket_id": ticket_id,
        "graphiti_episode_uuid": episode_uuid,
        "knowledge_inserted": inserted,
        "knowledge_updated": updated,
        "knowledge_total": len(merged_base),
        "status": "processed",
    })

    print("6/6 Base local e controle de incidentes atualizados.")
    print("\nProcessamento concluído com sucesso!")
    print(f"Ticket: {ticket_id}")
    print(f"Conhecimentos novos: {inserted}")
    print(f"Conhecimentos atualizados: {updated}")
    print(f"Total de conhecimentos na base: {len(merged_base)}")


def main():
    parser = argparse.ArgumentParser(
        description="Processa um ticket fechado e ingere conhecimento no Graphiti."
    )
    parser.add_argument(
        "ticket",
        help="Caminho do JSON do ticket, por exemplo: pipeline/ticket_2002.json"
    )
    args = parser.parse_args()

    asyncio.run(process_ticket(args.ticket))


if __name__ == "__main__":
    main()
