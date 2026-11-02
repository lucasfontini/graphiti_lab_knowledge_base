
import asyncio
import json
from pathlib import Path

from config import llm_client
from graphiti_core.llm_client.client import Message


# Diretório onde este arquivo está localizado
BASE_DIR = Path(__file__).resolve().parent


async def main():

    # 1. Ler o contexto preparado
    arquivo_contexto = BASE_DIR / "contexto_ticket.txt"

    with open(arquivo_contexto, "r", encoding="utf-8") as arquivo:
        contexto = arquivo.read()

    print("Ticket carregado!")
    print("Caracteres:", len(contexto))

    # 2. Criar o prompt para o LLM

    prompt = f"""
            Você é um analista especialista em troubleshooting de redes
            e telecomunicações.

            Analise o histórico completo do ticket e extraia conhecimentos
            relevantes para uma base de conhecimento do NOC.

            REGRAS IMPORTANTES:

            1. Nunca invente informações.
            2. Diferencie fatos confirmados de inferências.
            3. Toda informação deve possuir uma origem.
            4. Não transforme suspeitas em fatos.
            5. Não generalize conclusões de um único incidente.
            6. Preserve evidências técnicas.
            7. Ignore comentários administrativos sem valor técnico.

            CLASSIFICAÇÕES:

            - fact: informação explicitamente confirmada.
            - inference: conclusão derivada das evidências.
            - hypothesis: possibilidade ainda não confirmada.

            TIPOS DE CONHECIMENTO:

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

            Retorne exclusivamente JSON válido, seguindo esta estrutura:

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
                        "source_comment_id": ""
                    }}
                ]
            }}

            IMPORTANTE:
            - Cada item de knowledge deve representar uma informação.
            - source deve identificar quem forneceu a informação.
            - source_comment_id deve ser o ID do comentário original, quando disponível.
            - Para inferências, explique que são inferências.
            - operational_learning deve ser tratado como aprendizado candidato,
            não como regra universal comprovada.

            HISTÓRICO DO TICKET:

            {contexto}
            """


    # 3. Enviar o prompt para o Groq
    print("\nEnviando histórico para o Groq...")

    response = await llm_client.generate_response(
        messages=[
            Message(
                role="user",
                content=prompt
            )
        ]
    )

    # 4. Exibir o conhecimento extraído
    print("\nCONHECIMENTO EXTRAÍDO:\n")

    print(json.dumps(
        response,
        indent=4,
        ensure_ascii=False
    ))

    # 5. Salvar o resultado
    arquivo_saida = BASE_DIR / "conhecimento_extraido.json"

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        json.dump(
            response,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nArquivo gerado: {arquivo_saida}")


if __name__ == "__main__":
    asyncio.run(main())
