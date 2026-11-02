
import json

# 1. Ler o ticket
with open("ticket_simulado.json", "r", encoding="utf-8") as arquivo:
    ticket = json.load(arquivo)


# 2. Criar o contexto do ticket
contexto = f"""
TICKET: {ticket['ticket_id']}
ASSUNTO: {ticket['subject']}
STATUS: {ticket['status']}

CLIENTE: {ticket['customer']['name']}
CIRCUITO: {ticket['service']['circuit_id']}
SERVICO: {ticket['service']['type']}
PROVEDOR: {ticket['provider']['name']}

HISTORICO DE COMENTARIOS:
"""

# 3. Adicionar os comentários
for comentario in ticket["comments"]:

    contexto += f"""
[{comentario['timestamp']}]
Autor: {comentario['author']}
Origem: {comentario['source']}
Mensagem: {comentario['message']}
"""

# 4. Exibir o contexto preparado
print(contexto)

# 5. Salvar para inspeção
with open("contexto_ticket.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write(contexto)

print("\nContexto preparado com sucesso!")
