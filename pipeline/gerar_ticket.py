
import json
from datetime import datetime, timezone

ticket = {
    "ticket_id": "INC-2001",
    "subject": "Perda de pacotes no circuito CIR-1001",
    "status": "closed",
    "priority": "high",
    "created_at": "2026-10-30T14:32:00Z",
    "closed_at": "2026-10-30T18:00:00Z",

    "customer": {
        "name": "Acme Telecom",
        "customer_id": "CUS-1001"
    },

    "service": {
        "circuit_id": "CIR-1001",
        "type": "DIA",
        "bandwidth": "500 Mbps"
    },

    "provider": {
        "name": "Lumen"
    },

    "comments": [
        {
            "id": 1,
            "timestamp": "2026-10-30T14:32:00Z",
            "author": "Cliente",
            "source": "customer",
            "public": True,
            "message": "Estamos enfrentando lentidão e perda de pacotes na conexão. Favor verificar."
        },
        {
            "id": 2,
            "timestamp": "2026-10-30T14:40:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "Iniciando análise. Vamos verificar conectividade e interfaces."
        },
        {
            "id": 3,
            "timestamp": "2026-10-30T14:48:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "Ping para o CPE apresenta 15% de packet loss. Interface WAN sem erros físicos."
        },
        {
            "id": 4,
            "timestamp": "2026-10-30T15:05:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "Executado traceroute. Perda identificada no segmento da operadora."
        },
        {
            "id": 5,
            "timestamp": "2026-10-30T15:20:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "Aberto chamado com a Lumen: VND-8891."
        },
        {
            "id": 6,
            "timestamp": "2026-10-30T16:10:00Z",
            "author": "Suporte Lumen",
            "source": "provider",
            "public": False,
            "message": "Identificamos falha em uma placa de transmissão no equipamento de agregação. Equipe técnica atuando na substituição."
        },
        {
            "id": 7,
            "timestamp": "2026-10-30T17:25:00Z",
            "author": "Suporte Lumen",
            "source": "provider",
            "public": False,
            "message": "Substituição da placa concluída. Serviço normalizado."
        },
        {
            "id": 8,
            "timestamp": "2026-10-30T17:40:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "Testes de ping realizados. Sem perda de pacotes. Latência normalizada."
        },
        {
            "id": 9,
            "timestamp": "2026-10-30T17:50:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": False,
            "message": "RFO: Causa raiz: falha de hardware em placa de transmissão no equipamento de agregação da operadora Lumen. Substituição do componente restabeleceu o serviço."
        },
        {
            "id": 10,
            "timestamp": "2026-10-30T18:00:00Z",
            "author": "Analista NOC",
            "source": "noc",
            "public": True,
            "message": "Cliente informado e ticket encerrado."
        }
    ]
}

# Gerar arquivo JSON
with open("ticket_simulado.json", "w", encoding="utf-8") as arquivo:
    json.dump(ticket, arquivo, indent=4, ensure_ascii=False)

print("Ticket gerado com sucesso!")
