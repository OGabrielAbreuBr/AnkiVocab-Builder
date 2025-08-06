# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.staticfiles import StaticFiles

# Importe seus routers
from api.endpoints.vocab import router as vocab_router
from api.endpoints.anki import router as anki_router
from api.endpoints.decks import router as deck_router
from api.endpoints.login import router as login_router
from api.endpoints.users import router as users_router
from api.endpoints.languages import router as languages_router

# Importe a função para inicializar o DB e as configurações
from db.session import init_db
from core.config import settings  # Importa a instância das configurações

# Lifespan: A maneira moderna de lidar com eventos de startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INÍCIO DA DEPURAÇÃO ---
    # Esta linha vai nos mostrar qual URL está sendo usada antes de tentar a conexão
    print("--- INÍCIO DA DEPURAÇÃO ---")
    print(f"INFO:     Tentando conectar com a URL: {settings.database_url}")
    print("--- FIM DA DEPURAÇÃO ---")
    # --- FIM DO DEBUGGING ---

    # Código que roda ANTES da aplicação iniciar
    print("INFO:     Aplicação iniciando...")
    await init_db()
    print("INFO:     Banco de dados inicializado.")
    yield
    # Código que roda DEPOIS da aplicação terminar
    print("INFO:     Aplicação encerrando.")


# --- Instância principal do FastAPI ---
app = FastAPI(
    title="Vocabulary Expander API",
    description="API para expansão de vocabulário e geração de decks Anki.",
    version="1.0.0",
    lifespan=lifespan  # Associa o lifespan à aplicação
)


# --- Middlewares ---
# Configura o CORS para permitir que o frontend (ex: http://localhost:3000) acesse a API
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

# --- Routers da API ---
# É uma boa prática agrupar todos os endpoints sob um prefixo comum como /api/v1
api_prefix = "/api/v1"
app.include_router(vocab_router, prefix=api_prefix)
app.include_router(anki_router, prefix=api_prefix)
app.include_router(deck_router, prefix=api_prefix)
app.include_router(login_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(languages_router, prefix=api_prefix)

# Endpoint de "health check" para verificar se a API está no ar
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}