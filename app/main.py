from fastapi import FastAPI

from app import health
from app.errors import configure_error_handlers
from app.professionals import router as professionals
from app.reminders import router as reminders


def create_app() -> FastAPI:
    """Monta a aplicação. Os testes chamam esta função para subir a API."""
    app = FastAPI(title="Vaga Viva: clínica")
    configure_error_handlers(app)
    app.include_router(health.router)
    app.include_router(professionals.router)
    app.include_router(reminders.router)
    return app


app = create_app()
