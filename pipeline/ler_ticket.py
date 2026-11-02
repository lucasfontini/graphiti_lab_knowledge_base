
import json

# 1. Abrir o arquivo
with open("ticket_simulado.json", "r", encoding="utf-8") as arquivo:
    ticket = json.load(arquivo)

# 2. Exibir informações principais
print("Ticket:", ticket["ticket_id"])
print("Cliente:", ticket["customer"]["name"])
print("Circuito:", ticket["service"]["circuit_id"])
print("Status:", ticket["status"])

# 3. Percorrer todos os comentários
print("\nHISTORICO DO TICKET")

for comentario in ticket["comments"]:
    print(
        comentario["timestamp"],
        "|",
        comentario["source"],
        "|",
        comentario["message"]
    )
