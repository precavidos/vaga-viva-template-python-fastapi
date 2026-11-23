"""Acesso direto ao PostgreSQL dos testes, para dados de teste e conferências em SQL."""

from typing import Any

import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(self, url: str) -> None:
        self._connection = psycopg.connect(url, autocommit=True, row_factory=dict_row)

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall() if cursor.description else []

    def table_exists(self, table: str) -> bool:
        rows = self.query(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = %s",
            (table,),
        )
        return len(rows) > 0

    def columns(self, table: str) -> list[str]:
        rows = self.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = current_schema() AND table_name = %s",
            (table,),
        )
        return [row["column_name"] for row in rows]

    def reset(self) -> None:
        """Esvazia todas as tabelas, menos o histórico de migrações do Alembic."""
        rows = self.query(
            "SELECT quote_ident(tablename) AS name FROM pg_tables "
            "WHERE schemaname = current_schema() AND tablename <> 'alembic_version'"
        )
        if rows:
            self.query("SET lock_timeout = '10s'")
            self.query(f"TRUNCATE TABLE {', '.join(row['name'] for row in rows)} RESTART IDENTITY CASCADE")

    def insert_professional(self, name: str = "Dra. Helena Prado", specialty: str = "Clínica geral") -> int:
        rows = self.query("INSERT INTO professionals (name, specialty) VALUES (%s, %s) RETURNING id", (name, specialty))
        return rows[0]["id"]

    def insert_appointment(self, professional_id: int, patient_id: int, start: str, duration_minutes: int) -> int:
        """`start` é uma data e hora local, no formato `AAAA-MM-DDTHH:MM:SS`."""
        rows = self.query(
            "INSERT INTO appointments (professional_id, patient_id, starts_at, duration_minutes) "
            "VALUES (%s, %s, %s::timestamp, %s) RETURNING id",
            (professional_id, patient_id, start, duration_minutes),
        )
        return rows[0]["id"]

    def count_appointments(self) -> int:
        return self.query("SELECT count(*)::int AS count FROM appointments")[0]["count"]

    def close(self) -> None:
        self._connection.close()
