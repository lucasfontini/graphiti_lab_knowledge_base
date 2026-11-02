
import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def carregar(nome):
    caminho = BASE_DIR / nome

    if not caminho.exists():
        return []

    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar(nome, dados):
    with open(BASE_DIR / nome, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


def normalizar(texto):
    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


def criar_chave(item):
    return (
        item.get("circuit_id", ""),
        item.get("provider", ""),
        item.get("type", ""),
        normalizar(item.get("content", ""))
    )


def main():

    # 1. Carregar os dados existentes
    base = carregar("base_conhecimento.json")
    incidentes = carregar("incidentes.json")

    novos = carregar("conhecimento_validado.json")
    ticket = carregar("conhecimento_extraido.json")

    ticket_id = ticket["ticket_id"]
    circuit_id = ticket["circuit_id"]
    provider = ticket["provider"]

    # 2. Verificar se o incidente já foi processado
    incidente_existente = any(
        item["ticket_id"] == ticket_id
        for item in incidentes
    )

    if incidente_existente:
        print(f"Ticket {ticket_id} já foi processado.")
        print("Nenhuma alteração realizada.")
        return

    # 3. Criar índice dos conhecimentos existentes
    indice = {
        criar_chave(item): item
        for item in base
    }

    inseridos = 0
    atualizados = 0

    # 4. Processar os conhecimentos
    for item in novos:

        item["circuit_id"] = circuit_id
        item["provider"] = provider

        chave = criar_chave(item)

        if chave in indice:

            existente = indice[chave]

            # Recuperar histórico de origens
            if "source_tickets" not in existente:
                existente["source_tickets"] = [
                    existente.pop("source_ticket", "")
                ]

            # Adicionar novo ticket sem duplicar
            if ticket_id not in existente["source_tickets"]:
                existente["source_tickets"].append(ticket_id)

            existente["occurrences"] = len(
                existente["source_tickets"]
            )

            atualizados += 1

        else:

            item["source_tickets"] = [ticket_id]
            item["occurrences"] = 1

            base.append(item)
            indice[chave] = item

            inseridos += 1

    # 5. Registrar o incidente separadamente
    incidentes.append({
        "ticket_id": ticket_id,
        "circuit_id": circuit_id,
        "provider": provider,
        "status": "processed"
    })

    # 6. Persistir os dados
    salvar("base_conhecimento.json", base)
    salvar("incidentes.json", incidentes)

    print("\nProcessamento concluído!")
    print("Conhecimentos inseridos:", inseridos)
    print("Conhecimentos atualizados:", atualizados)
    print("Total na base:", len(base))
    print("Total de incidentes:", len(incidentes))


if __name__ == "__main__":
    main()
