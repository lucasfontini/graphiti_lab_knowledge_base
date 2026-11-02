
import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def normalizar(texto):
    """Normaliza texto para comparação exata."""
    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        char for char in texto
        if unicodedata.category(char) != "Mn"
    )

    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


def criar_chave(item):
    """Cria uma identidade determinística para o conhecimento."""

    return (
        item.get("circuit_id", ""),
        item.get("provider", ""),
        item.get("type", ""),
        normalizar(item.get("content", ""))
    )


# 1. Carregar os dados
with open(BASE_DIR / "base_conhecimento.json", encoding="utf-8") as f:
    base = json.load(f)

with open(BASE_DIR / "conhecimento_validado.json", encoding="utf-8") as f:
    dados = json.load(f)

# 2. Recuperar os dados gerais do ticket
with open(BASE_DIR / "conhecimento_extraido.json", encoding="utf-8") as f:
    ticket = json.load(f)

circuit_id = ticket["circuit_id"]
provider = ticket["provider"]
ticket_id = ticket["ticket_id"]

# 3. Preparar as chaves existentes
chaves_existentes = {
    criar_chave(item)
    for item in base
}

novos = []
duplicados = []

# 4. Comparar os conhecimentos
for item in dados:

    # Enriquecer com os dados do ticket
    item["circuit_id"] = circuit_id
    item["provider"] = provider
    item["source_ticket"] = ticket_id

    chave = criar_chave(item)
    print(chave)

    if chave in chaves_existentes:
        duplicados.append(item)
    else:
        novos.append(item)
        chaves_existentes.add(chave)


# 5. Exibir resultado
print("Conhecimentos recebidos:", len(dados))
print("Conhecimentos duplicados:", len(duplicados))
print("Conhecimentos novos:", len(novos))

# 6. Salvar resultados
with open(BASE_DIR / "novos_conhecimentos.json", "w", encoding="utf-8") as f:
    json.dump(novos, f, indent=4, ensure_ascii=False)

with open(BASE_DIR / "duplicados.json", "w", encoding="utf-8") as f:
    json.dump(duplicados, f, indent=4, ensure_ascii=False)

print("\nArquivos gerados:")
print("novos_conhecimentos.json")
print("duplicados.json")
