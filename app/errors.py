from fastapi import FastAPI


def configure_error_handlers(app: FastAPI) -> None:
    """Registra os tratadores de erro da aplicação."""
