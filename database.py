"""
=============================================================================
CAMADA DE PERSISTÊNCIA (PostgreSQL / Supabase)
=============================================================================
Toda a comunicação com o banco de dados acontece aqui.
Nenhuma lógica de UI deve estar neste arquivo.

Contratos:
- Todas as funções capturam exceções e retornam None/False/list vazia
- Nunca levantam exceção para o usuário final
- Logging via módulo logging
- Conexão lida de st.secrets["DATABASE_URL"]
=============================================================================
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# CONSTANTE DE CONEXÃO
# -----------------------------------------------------------------------------
DATABASE_URL = st.secrets["DATABASE_URL"]


# =============================================================================
# CONEXÃO
# =============================================================================
def _conectar() -> psycopg2.extensions.connection:
    """
    Abre conexão com o PostgreSQL (Supabase).
    Usa RealDictCursor para que os resultados venham como dicionários.
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


# =============================================================================
# CRIAÇÃO DA TABELA
# =============================================================================
def init_database() -> None:
    """
    Cria a tabela `sessoes_estudo` se ainda não existir.
    Também cria os índices. Idempotente.
    """
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessoes_estudo (
                        id          SERIAL PRIMARY KEY,
                        data        DATE    NOT NULL,
                        disciplina  TEXT    NOT NULL,
                        topico      TEXT    NOT NULL,
                        horas       REAL    NOT NULL DEFAULT 0,
                        questoes    INTEGER NOT NULL DEFAULT 0,
                        acertos     INTEGER NOT NULL DEFAULT 0,
                        erros       INTEGER NOT NULL DEFAULT 0,
                        observacoes TEXT,
                        criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Índices para acelerar consultas
                cur.execute("CREATE INDEX IF NOT EXISTS idx_data ON sessoes_estudo(data)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_disciplina ON sessoes_estudo(disciplina)")
                conn.commit()
                logger.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logger.error("Erro ao inicializar banco: %s", e)


# =============================================================================
# INSERT
# =============================================================================
def inserir_sessao(
    data: str,
    disciplina: str,
    topico: str,
    horas: float,
    questoes: int,
    acertos: int,
    erros: Optional[int] = None,
    observacoes: str = "",
) -> Optional[int]:
    """
    Insere uma nova sessão de estudo.

    Parâmetros:
        data         : string ISO (YYYY-MM-DD)
        disciplina   : nome exato da disciplina
        topico       : tópico dentro da disciplina
        horas        : horas estudadas (float, aceita 0.5 = 30min)
        questoes     : total de questões resolvidas
        acertos      : total de acertos
        erros        : opcional; se None, calcula como questoes - acertos
        observacoes  : texto livre

    Retorna:
        id da linha inserida, ou None em caso de erro.
    """
    try:
        if erros is None:
            erros = max(questoes - acertos, 0)
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessoes_estudo
                        (data, disciplina, topico, horas, questoes, acertos, erros, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (data, disciplina, topico, float(horas), int(questoes),
                      int(acertos), int(erros), observacoes))
                novo_id = cur.fetchone()["id"]
                conn.commit()
                logger.info("Sessão inserida com id=%s", novo_id)
                return novo_id
    except Exception as e:
        logger.error("Erro ao inserir sessão: %s", e)
        return None


# =============================================================================
# SELECT (com filtros)
# =============================================================================
def listar_sessoes(filtros: Optional[dict[str, Any]] = None) -> list[dict]:
    """
    Lista sessões aplicando filtros opcionais.

    filtros aceitos:
        data_inicio : 'YYYY-MM-DD'
        data_fim    : 'YYYY-MM-DD'
        disciplina  : string exata
        topico      : string exata
        limite      : int (default 500)

    Retorna lista de dicts (uma linha por sessão), ordenada por data DESC.
    """
    filtros = filtros or {}
    sql = "SELECT * FROM sessoes_estudo WHERE 1=1"
    params: list[Any] = []

    if filtros.get("data_inicio"):
        sql += " AND data >= %s"
        params.append(filtros["data_inicio"])
    if filtros.get("data_fim"):
        sql += " AND data <= %s"
        params.append(filtros["data_fim"])
    if filtros.get("disciplina"):
        sql += " AND disciplina = %s"
        params.append(filtros["disciplina"])
    if filtros.get("topico"):
        sql += " AND topico = %s"
        params.append(filtros["topico"])

    sql += " ORDER BY data DESC, id DESC LIMIT %s"
    params.append(int(filtros.get("limite", 500)))

    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        logger.error("Erro ao listar sessões: %s", e)
        return []


# =============================================================================
# UPDATE
# =============================================================================
def atualizar_sessao(id_: int, dados: dict[str, Any]) -> bool:
    """
    Atualiza campos de uma sessão. Aceita qualquer subconjunto de campos.
    Retorna True se atualizou, False caso contrário.
    """
    campos_permitidos = {
        "data", "disciplina", "topico", "horas",
        "questoes", "acertos", "erros", "observacoes"
    }
    campos = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not campos:
        return False

    # Recalcula erros se questoes/acertos foram alterados e erros não veio explícito
    if ("questoes" in campos or "acertos" in campos) and "erros" not in campos:
        try:
            with _conectar() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT questoes, acertos FROM sessoes_estudo WHERE id = %s", (id_,))
                    row = cur.fetchone()
                    if row:
                        q = campos.get("questoes", row["questoes"])
                        a = campos.get("acertos", row["acertos"])
                        campos["erros"] = max(q - a, 0)
        except Exception:
            pass

    set_clause = ", ".join(f"{k} = %s" for k in campos.keys())
    valores = list(campos.values()) + [id_]

    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE sessoes_estudo SET {set_clause} WHERE id = %s", valores)
                conn.commit()
                ok = cur.rowcount > 0
                logger.info("Sessão %s atualizada: %s", id_, ok)
                return ok
    except Exception as e:
        logger.error("Erro ao atualizar sessão %s: %s", id_, e)
        return False


# =============================================================================
# DELETE
# =============================================================================
def deletar_sessao(id_: int) -> bool:
    """Remove uma sessão pelo ID. Retorna True se removeu."""
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sessoes_estudo WHERE id = %s", (id_,))
                conn.commit()
                ok = cur.rowcount > 0
                logger.info("Sessão %s deletada: %s", id_, ok)
                return ok
    except Exception as e:
        logger.error("Erro ao deletar sessão %s: %s", id_, e)
        return False


# =============================================================================
# AGREGAÇÕES / ESTATÍSTICAS
# =============================================================================
def obter_estatisticas_gerais() -> dict:
    """
    Retorna KPIs gerais:
        total_horas, total_questoes, total_acertos, total_erros,
        percentual_acerto, dias_estudados
    """
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COALESCE(SUM(horas), 0)     AS total_horas,
                        COALESCE(SUM(questoes), 0)  AS total_questoes,
                        COALESCE(SUM(acertos), 0)   AS total_acertos,
                        COALESCE(SUM(erros), 0)     AS total_erros,
                        COUNT(DISTINCT data)        AS dias_estudados
                    FROM sessoes_estudo
                """)
                row = dict(cur.fetchone())
                total_q = row["total_acertos"] + row["total_erros"]
                row["percentual_acerto"] = (row["total_acertos"] / total_q) if total_q else 0.0
                return row
    except Exception as e:
        logger.error("Erro em obter_estatisticas_gerais: %s", e)
        return {
            "total_horas": 0, "total_questoes": 0, "total_acertos": 0,
            "total_erros": 0, "percentual_acerto": 0.0, "dias_estudados": 0,
        }


def obter_estatisticas_por_disciplina() -> list[dict]:
    """
    Retorna lista com uma linha por disciplina:
        disciplina, horas, questoes, acertos, erros, percentual_acerto
    """
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        disciplina,
                        COALESCE(SUM(horas), 0)    AS horas,
                        COALESCE(SUM(questoes), 0) AS questoes,
                        COALESCE(SUM(acertos), 0)  AS acertos,
                        COALESCE(SUM(erros), 0)    AS erros
                    FROM sessoes_estudo
                    GROUP BY disciplina
                    ORDER BY horas DESC
                """)
                resultado = []
                for row in cur.fetchall():
                    d = dict(row)
                    total = d["acertos"] + d["erros"]
                    d["percentual_acerto"] = (d["acertos"] / total) if total else 0.0
                    resultado.append(d)
                return resultado
    except Exception as e:
        logger.error("Erro em obter_estatisticas_por_disciplina: %s", e)
        return []


def obter_estatisticas_por_topico(disciplina: Optional[str] = None) -> list[dict]:
    """
    Retorna estatísticas agrupadas por (disciplina, tópico).
    Se `disciplina` for informada, filtra apenas ela.
    """
    try:
        sql = """
            SELECT
                disciplina,
                topico,
                COALESCE(SUM(horas), 0)    AS horas,
                COALESCE(SUM(questoes), 0) AS questoes,
                COALESCE(SUM(acertos), 0)  AS acertos,
                COALESCE(SUM(erros), 0)    AS erros
            FROM sessoes_estudo
        """
        params: list[Any] = []
        if disciplina:
            sql += " WHERE disciplina = %s"
            params.append(disciplina)
        sql += " GROUP BY disciplina, topico ORDER BY disciplina, horas DESC"

        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                resultado = []
                for row in cur.fetchall():
                    d = dict(row)
                    total = d["acertos"] + d["erros"]
                    d["percentual_acerto"] = (d["acertos"] / total) if total else 0.0
                    resultado.append(d)
                return resultado
    except Exception as e:
        logger.error("Erro em obter_estatisticas_por_topico: %s", e)
        return []


def obter_estatisticas_diarias(dias: int = 60) -> list[dict]:
    """
    Retorna, por dia (últimos `dias` dias), soma de horas e questões.
    Útil para o gráfico de linha do dashboard.
    """
    try:
        data_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        data,
                        COALESCE(SUM(horas), 0)    AS horas,
                        COALESCE(SUM(questoes), 0) AS questoes,
                        COALESCE(SUM(acertos), 0)  AS acertos
                    FROM sessoes_estudo
                    WHERE data >= %s
                    GROUP BY data
                    ORDER BY data ASC
                """, (data_limite,))
                resultado = []
                for row in cur.fetchall():
                    d = dict(row)
                    total = d["questoes"]
                    d["percentual_acerto"] = (d["acertos"] / total) if total else 0.0
                    resultado.append(d)
                return resultado
    except Exception as e:
        logger.error("Erro em obter_estatisticas_diarias: %s", e)
        return []


def obter_estatisticas_semanais(semanas: int = 12) -> list[dict]:
    """
    Retorna agregado semanal (segunda a domingo) das últimas `semanas`.
    """
    try:
        data_limite = (datetime.now() - timedelta(weeks=semanas)).strftime("%Y-%m-%d")
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        TO_CHAR(data, 'IYYY-IW') AS semana,
                        MIN(data) AS data_inicio,
                        MAX(data) AS data_fim,
                        COALESCE(SUM(horas), 0)    AS horas,
                        COALESCE(SUM(questoes), 0) AS questoes,
                        COALESCE(SUM(acertos), 0)  AS acertos,
                        COALESCE(SUM(erros), 0)    AS erros
                    FROM sessoes_estudo
                    WHERE data >= %s
                    GROUP BY semana
                    ORDER BY semana ASC
                """, (data_limite,))
                resultado = []
                for row in cur.fetchall():
                    d = dict(row)
                    total = d["acertos"] + d["erros"]
                    d["percentual_acerto"] = (d["acertos"] / total) if total else 0.0
                    resultado.append(d)
                return resultado
    except Exception as e:
        logger.error("Erro em obter_estatisticas_semanais: %s", e)
        return []


def obter_sessao(id_: int) -> Optional[dict]:
    """Retorna uma sessão pelo ID, ou None."""
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM sessoes_estudo WHERE id = %s", (id_,))
                row = cur.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error("Erro em obter_sessao: %s", e)
        return None


# =============================================================================
# EXECUÇÃO DIRETA (para testes)
# =============================================================================
if __name__ == "__main__":
    init_database()
    print("✅ Banco inicializado com sucesso.")
    print("📊 Estatísticas gerais:", obter_estatisticas_gerais())