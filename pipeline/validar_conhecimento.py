
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. Carregar conhecimento extraído
with open(
    BASE_DIR / "conhecimento_extraido.json",
    "r",
    encoding="utf-8"
) as arquivo:
    dados = json.load(arquivo)


# 2. Validar cada conhecimento
conhecimentos_validos = []

for item in dados["knowledge"]:

    erros = []

    if not item.get("content"):
        erros.append("Conteúdo vazio")

    if item.get("classification") not in [
        "fact", "inference", "hypothesis"
    ]:
        erros.append("Classificação inválida")

    if item.get("type") not in [
        "symptom",
        "technical_evidence",
        "root_cause",
        "action",
        "resolution",
        "operational_learning"
    ]:
        erros.append("Tipo inválido")

    if not item.get("source"):
        erros.append("Origem não informada")

    if erros:
        print("Conhecimento rejeitado:", erros)
        continue

    conhecimentos_validos.append(item)


# 3. Separar fatos e inferências
fatos = [
    item for item in conhecimentos_validos
    if item["classification"] == "fact"
]

inferencias = [
    item for item in conhecimentos_validos
    if item["classification"] == "inference"
]


# 4. Mostrar resultado
print("Total recebido:", len(dados["knowledge"]))
print("Conhecimentos válidos:", len(conhecimentos_validos))
print("Fatos:", len(fatos))
print("Inferências:", len(inferencias))


# 5. Salvar resultado validado
with open(
    BASE_DIR / "conhecimento_validado.json",
    "w",
    encoding="utf-8"
) as arquivo:
    json.dump(
        conhecimentos_validos,
        arquivo,
        indent=4,
        ensure_ascii=False
    )

print("\nConhecimento validado salvo!")
