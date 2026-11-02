import asyncio

from config import llm_client
from graphiti_core.llm_client.client import Message


async def main():
    response = await llm_client.generate_response(
        messages=[
            Message(
    role="user",
    content="Responda em JSON. Explique em uma frase o que e um circuito de internet DIA."
)
        ]
    )

    print("\nResposta do Groq:")
    print(response)


asyncio.run(main())