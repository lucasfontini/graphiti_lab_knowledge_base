# 🧠 Graphiti Lab — Knowledge Base

Laboratório prático de construção de uma **Base de Conhecimento Viva (Knowledge Graph)** utilizando Python, [Graphiti](https://github.com/getzep/graphiti) e Neo4j.

O objetivo é transformar informações operacionais, como tickets, conversas, e-mails e dados de infraestrutura, em conhecimento estruturado, contextual e relacionado temporalmente.

## 🎯 Objetivos do projeto

- Aprender Graphiti do básico ao avançado.
- Entender como episódios são transformados em entidades e relacionamentos.
- Construir um Knowledge Graph utilizando Neo4j.
- Extrair conhecimento de tickets e conversas com modelos LLM.
- Relacionar clientes, circuitos, fornecedores e incidentes.
- Identificar recorrência de problemas e causas raiz.
- Criar uma base de conhecimento que possa ser consultada por agentes de IA.

## 🏗️ Arquitetura

### Laboratório atual

O laboratório utiliza Python para inserir episódios no Graphiti, que processa as informações e atualiza o grafo armazenado no Neo4j.

```text
        Python
          |
          v
       Graphiti
          |
          v
         LLM
       (Groq)
          |
          v
      Embeddings
      (Gemini)
          |
          v
        Neo4j
          |
          v
    Knowledge Graph
```

### Arquitetura futura — Knowledge Ingestion Pipeline

A evolução planejada é coletar dados automaticamente de diferentes fontes e processá-los de maneira incremental.

```text
  Zendesk   WhatsApp   E-mail   NetBox
      \        |        |       /
       \       |        |      /
              n8n
               |
            RabbitMQ
               |
         Python Worker
               |
         Normalização
               |
        Extração com LLM
               |
     Validação e Deduplicação
               |
             Graphiti
               |
             Neo4j
               |
       Knowledge Graph
               |
        Agentes de IA
```

## 🧰 Tecnologias utilizadas

| Tecnologia | Responsabilidade |
|---|---|
| Python | Processamento e integração |
| Graphiti | Construção e atualização do grafo |
| Neo4j | Banco de dados orientado a grafos |
| Groq | Extração e interpretação de informações |
| Gemini | Embeddings e reranking |
| uv | Gerenciamento do ambiente Python |
| n8n | Futuro mecanismo de coleta |
| RabbitMQ | Futuro transporte de eventos |

## 📁 Estrutura do projeto

```text
graphiti_lab_knowledge_base/
│
├── config.py
├── main.py
├── seed.py
│
├── insert_episodes.py
├── insert_ticket.py
├── inspect_grafo.py
├── test_grok.py
│
├── pyproject.toml
├── uv.lock
└── README.md
```

### Descrição dos arquivos

| Arquivo | Descrição |
|---|---|
| `config.py` | Configuração dos clientes Groq, Gemini Embedder e Gemini Reranker |
| `main.py` | Exemplo de configuração e inicialização dos componentes |
| `seed.py` | Insere episódios fictícios de circuitos, tickets e e-mails |
| `insert_episodes.py` | Demonstra inserção de um episódio de cadastro de circuito |
| `insert_ticket.py` | Demonstra inserção de um episódio de ticket |
| `inspect_grafo.py` | Consulta nós e relacionamentos diretamente no Neo4j |
| `test_grok.py` | Testa comunicação com o modelo Groq |

## ⚙️ Instalação

### Pré-requisitos

- Python 3.12 ou superior.
- Neo4j Community ou Enterprise.
- [uv](https://docs.astral.sh/uv/).
- Chaves de API da Groq e Google Gemini.

Clone o repositório:

```powershell
git clone https://github.com/lucasfontini/graphiti_lab_knowledge_base.git

cd graphiti_lab_knowledge_base
```

Instale as dependências:

```powershell
uv sync
```

## 🔐 Configuração das credenciais

Crie um arquivo `.env` na raiz do projeto:

```dotenv
GROQ_API_KEY=sua_chave_groq
GEMINI_API_KEY=sua_chave_gemini

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=sua_senha
```

O arquivo `config.py` carrega as variáveis de ambiente e inicializa os clientes.

Configuração utilizada:

| Componente | Modelo |
|---|---|
| LLM Groq | `openai/gpt-oss-120b` |
| Gemini Embedder | `gemini-embedding-001` |
| Gemini Reranker | `gemini-2.5-flash` |

**Importante:** nunca publique o arquivo `.env`, tokens, senhas ou dados reais de clientes. Configure o `.gitignore` para excluir esses arquivos.

## ▶️ Executando o laboratório

### 1. Testar o Groq

```powershell
uv run python test_grok.py
```

Verifica se o modelo consegue receber uma mensagem e retornar uma resposta.

### 2. Inserir um episódio

```powershell
uv run python insert_episodes.py
```

Exemplo: cadastro de um circuito associado a cliente e fornecedor.

### 3. Inserir um ticket

```powershell
uv run python insert_ticket.py
```

Demonstra como representar um ticket como episódio no Graphiti.

### 4. Executar o Seed

```powershell
uv run python seed.py
```

O seed cria um conjunto de dados fictícios contendo:

- 5 circuitos;
- 8 tickets;
- 3 e-mails de fornecedores.

Total: 16 episódios de laboratório.

O script utiliza `group_id="vendor-lab-demo"` e verifica se já existe um episódio com o mesmo nome e grupo antes de inserir.

### 5. Inspecionar o grafo

```powershell
uv run python inspect_grafo.py
```

Consulta os nós e relacionamentos existentes no Neo4j.

## 🧠 Conceitos importantes do Graphiti

### Episódios

Um episódio representa uma fonte de informação ou acontecimento que será processado pelo Graphiti.

Exemplos:

- Cadastro de circuito.
- Ticket de incidente.
- E-mail de fornecedor.
- Conversa com cliente.
- Relatório de causa raiz.

### Entidades

São os elementos identificados nas informações:

- Customer
- Provider
- Service
- Ticket
- Incident
- RootCause
- Region

### Relacionamentos

Representam conexões entre as entidades.

Exemplo:

```text
Customer
   |
   | OWNS
   v
Service
   |
   | MANAGED_BY
   v
Provider

Ticket
   |
   | AFFECTS
   v
Service
```

### Group ID

O `group_id` permite organizar os episódios em grupos lógicos.

Exemplos utilizados no laboratório:

```python
group_id="vendor-lab-demo"
group_id="vendor-lab"
group_id="noc"
```

O `group_id` ajuda a organizar e filtrar os dados, mas não representa isolamento físico nem controle de autorização no Neo4j.

## 📡 Próxima fase: Base de Conhecimento Viva

A próxima etapa é construir um pipeline capaz de coletar informações automaticamente e atualizar o grafo.

### Etapas planejadas

**1. Coleta**

Integrar fontes como:

- Zendesk.
- WhatsApp.
- E-mail.
- NetBox.
- APIs de provedores.

**2. Normalização**

Padronizar datas, IDs, nomes e estruturas de dados, preservando os registros originais.

**3. Extração com LLM**

Utilizar Groq para identificar:

- Fatos.
- Inferências.
- Hipóteses.
- Entidades.
- Eventos.
- Causas raiz.
- Evidências.

**4. Validação**

Verificar se as informações extraídas possuem estrutura correta e referências válidas às fontes.

**5. Deduplicação**

Identificar informações repetidas sem perder o histórico de ocorrências e fontes.

**6. Ingestão Graphiti**

Criar episódios e relacionamentos no Knowledge Graph.

**7. Consulta**

Permitir que agentes de IA recuperem informações históricas e contextuais.

## 🔍 Exemplos de perguntas que a base deverá responder

- Quais circuitos da Lumen apresentaram problemas nos últimos 30 dias?
- Quais fornecedores apresentam maior recorrência de falhas?
- O circuito CIR-1001 já apresentou problemas semelhantes?
- Qual foi a causa raiz do último incidente?
- Quais incidentes estão relacionados a uma mesma região?
- Quais clientes podem ser afetados por uma falha de infraestrutura?

## 🗺️ Roadmap

| Fase | Objetivo | Status |
|---|---|---|
| 1 | Fundamentos do Graphiti e Neo4j | Em desenvolvimento |
| 2 | Inserção de episódios | Implementado |
| 3 | Relacionamento entre entidades | Em laboratório |
| 4 | Extração automática com LLM | Em desenvolvimento |
| 5 | Validação e deduplicação | Em desenvolvimento |
| 6 | Pipeline de ingestão de tickets | Próxima etapa |
| 7 | Integração com RabbitMQ e n8n | Planejado |
| 8 | Base de conhecimento viva | Planejado |
| 9 | Consulta por agentes de IA | Planejado |

## 📚 Documentação e referências

- [Graphiti — GitHub oficial](https://github.com/getzep/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Graphiti Documentation](https://help.getzep.com/graphiti)
- [Groq Documentation](https://console.groq.com/docs)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)

---

**Princípio do projeto:** não queremos apenas armazenar tickets e conversas. Queremos transformar informações operacionais dispersas em conhecimento contextual, conectado, temporal e continuamente atualizado.