# AnkiVocab-Builder

backend/
├── app/
│   ├── main.py             # entrypoint FastAPI
│   ├── core/
│   │   └── config.py       # settings via Pydantic BaseSettings
│   ├── clients/
│   │   └── gemini_client.py
│   ├── services/
│   │   └── vocab_service.py
│   ├── api/
│   │   ├── deps.py         # dependências (DI)
│   │   └── endpoints/
│   │       └── vocab.py
│   ├── db/
│   │   ├── base.py         # engine, sessionmaker
│   │   └── repository.py   # CRUD genérico ou específico
│   └── schemas/
│       ├── word.py         # Pydantic models de request/response
│       └── anki.py         # modelo para .apkg
├── tests/
│   ├── conftest.py         # fixtures pytest
│   └── test_vocab.py
├── utils/
│   └── helpers.py          # funções transversais (e.g. serialização)
├── requirements.txt
└── Dockerfile

# Passos de execução

baixar imagem docker:

docker compose up -d
docker ps

python -m db.seed

Rodar servidor fast api seguindo o passo a passo abaixo:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

python -m http.server 3000

abrir:
http://localhost:3000   

# visualização da base de dados
Abra o seu terminal e execute o comando para entrar no cliente psql dentro do seu contentor

docker exec -it vocab-db psql -U usuario -d vocabdb

ma vez lá dentro (o seu terminal mudará para vocabdb=#), pode usar comandos para explorar:

\dt: Lista todas as tabelas.

SELECT * FROM users;: Mostra todos os dados da tabela de utilizadores.

\q: Sai do psql.

# resetar bd

Para resetar a sua base de dados:

docker compose down

APAGUE o volume de dados: 
docker volume rm app_postgres_data




