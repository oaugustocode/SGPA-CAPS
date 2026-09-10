"""Camada única de acesso e persistência no banco SQLite do SGDA-CAPS.

Para recriar a base de testes com registros fictícios, execute:
    python -m database.Seed
"""

from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import sqlite3

# Localização do arquivo SQLite relativo à pasta da camada de banco
caminhoBanco = Path(__file__).resolve().parent / "BancoSistemaArquivos.db"
limiteProntuariosPorCaixa = 20


def _garantirTabelaLogs(con: sqlite3.Connection) -> None:
    """Cria a tabela de log de ações caso ainda não exista (migração não destrutiva)."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS log_acoes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo        TEXT    NOT NULL CHECK (tipo IN ('REABERTO', 'ARQUIVADO')),
            nomePaciente    TEXT NOT NULL,
            dataNascimento  TEXT,
            caixaCodigo     TEXT,
            caixaSexo       TEXT,
            dataHora        TEXT NOT NULL
        )
        """
    )


@contextmanager
def conexao():
    """Abre uma conexão transacional e garante seu fechamento ao final do uso."""
    con = sqlite3.connect(caminhoBanco)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    _garantirTabelaLogs(con)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()



# ─── Consultas ─────────────────────────────────────────────────────────────────


def buscarProntuariosPorNomeOuCNS(termo, limite=8):
    # Normaliza o termo de busca removendo espaços extras
    texto = " ".join(str(termo).strip().split())
    if not texto:
        return []

    with conexao() as con:
        # Busca por correspondência parcial no nome do paciente ou no número do CNS
        return con.execute(
            """
            SELECT
                p.id,
                p.nome_paciente AS nomePaciente,
                p.data_nascimento AS dataNascimento,
                p.CNS AS cns,
                c.codigo AS caixaCodigo,
                c.sexo AS caixaSexo
            FROM prontuarios_antigos AS p
            LEFT JOIN caixas AS c ON c.id = p.caixasId
            WHERE p.nome_paciente COLLATE NOCASE LIKE ?
               OR p.CNS LIKE ?
            ORDER BY p.nome_paciente COLLATE NOCASE
            LIMIT ?
            """,
            (f"%{texto}%", f"%{texto}%", limite),
        ).fetchall()


def sugerirProntuarios(nome, limite=8):
    # Atalho para autocompletar sugestões durante a digitação na busca
    return buscarProntuariosPorNomeOuCNS(nome, limite)


def buscarProntuario(prontuarioId):
    # Retorna o registro completo de um prontuário específico pelo seu ID
    with conexao() as con:
        return con.execute(
            """
            SELECT
                p.id,
                p.nome_paciente AS nomePaciente,
                p.nome_pai AS nomePai,
                p.nome_mae AS nomeMae,
                p.data_nascimento AS dataNascimento,
                p.sexo AS sexo,
                p.CNS AS cns,
                c.codigo AS caixaCodigo,
                c.sexo AS caixaSexo
            FROM prontuarios_antigos AS p
            LEFT JOIN caixas AS c ON c.id = p.caixasId
            WHERE p.id = ?
            """,
            (prontuarioId,),
        ).fetchone()


def contarCaixas(sexo, letra=None):
    # Conta a quantidade total de caixas cadastradas para cálculo da paginação
    filtroLetra = f"{letra}%" if letra else "%"
    with conexao() as con:
        resultado = con.execute(
            """
            SELECT COUNT(*) AS total
            FROM caixas
            WHERE sexo COLLATE NOCASE LIKE ?
              AND CAST(codigo AS TEXT) LIKE ?
            """,
            (f"{sexo}%", filtroLetra),
        ).fetchone()
        return resultado["total"] if resultado else 0


def buscarCaixasComProntuariosPaginado(sexo, letra=None, limite=6, offset=0):
    filtroLetra = f"{letra}%" if letra else "%"

    with conexao() as con:
        # Busca o lote de caixas referente à página solicitada
        caixas = con.execute(
            """
            SELECT id, codigo, sexo
            FROM caixas
            WHERE sexo COLLATE NOCASE LIKE ?
              AND CAST(codigo AS TEXT) LIKE ?
            ORDER BY codigo
            LIMIT ? OFFSET ?
            """,
            (f"{sexo}%", filtroLetra, limite, offset),
        ).fetchall()

        if not caixas:
            return []

        prontuariosPorCaixa = {}
        idsCaixas = [caixa["id"] for caixa in caixas]
        marcadores = ", ".join("?" for _ in idsCaixas)

        # Utiliza Window Function (ROW_NUMBER) para limitar prontuários por caixa a 20 e evitar carga excessiva
        prontuarios = con.execute(
            f"""
            WITH prontuarios_limitados AS (
                SELECT
                    p.caixasId,
                    p.nome_paciente AS nomePaciente,
                    p.nome_pai AS nomePai,
                    p.nome_mae AS nomeMae,
                    p.data_nascimento AS dataNascimento,
                    p.sexo AS sexo,
                    p.CNS AS cns,
                    ROW_NUMBER() OVER (
                        PARTITION BY p.caixasId
                        ORDER BY p.nome_paciente COLLATE NOCASE, p.id
                    ) AS linha
                FROM prontuarios_antigos AS p
                LEFT JOIN caixas AS c ON c.id = p.caixasId
                WHERE p.caixasId IN ({marcadores})
            )
            SELECT
                caixasId,
                nomePaciente,
                nomePai,
                nomeMae,
                dataNascimento,
                sexo,
                cns
            FROM prontuarios_limitados
            WHERE linha <= ?
            ORDER BY caixasId, nomePaciente COLLATE NOCASE
            """,
            (*idsCaixas, limiteProntuariosPorCaixa),
        ).fetchall()

        for prontuario in prontuarios:
            prontuariosPorCaixa.setdefault(prontuario["caixasId"], []).append(prontuario)

    # Agrupa as caixas com seus respectivos prontuários vinculados
    return [
        {
            "id": caixa["id"],
            "codigo": caixa["codigo"],
            "sexo": caixa["sexo"],
            "prontuarios": prontuariosPorCaixa.get(caixa["id"], []),
        }
        for caixa in caixas
    ]


# ─── Escrita ───────────────────────────────────────────────────────────────────


def listarCaixas(sexo=None):
    """Retorna todas as caixas, opcionalmente filtradas por sexo para seleção nos formulários."""
    with conexao() as con:
        if sexo:
            return con.execute(
                "SELECT id, codigo, sexo FROM caixas WHERE sexo = ? ORDER BY codigo",
                (sexo,),
            ).fetchall()
        return con.execute(
            "SELECT id, codigo, sexo FROM caixas ORDER BY sexo, codigo"
        ).fetchall()


def listarProntuariosPorCaixa(caixaId):
    """Retorna os prontuários de uma caixa para preenchimento da seleção."""
    with conexao() as con:
        return con.execute(
            """
            SELECT id, nome_paciente AS nomePaciente, data_nascimento AS dataNascimento, CNS AS cns
            FROM prontuarios_antigos
            WHERE caixasId = ?
            ORDER BY nome_paciente COLLATE NOCASE, id
            """,
            (caixaId,),
        ).fetchall()


def excluirProntuario(prontuarioId):
    """Exclui um prontuário pelo identificador e informa se houve remoção."""
    with conexao() as con:
        cursor = con.execute("DELETE FROM prontuarios_antigos WHERE id = ?", (prontuarioId,))
        return cursor.rowcount > 0


def criarCaixa(codigo, sexo):
    """Cria uma nova caixa arquivística no banco e retorna o ID gerado."""
    with conexao() as con:
        cursor = con.execute(
            "INSERT INTO caixas (codigo, sexo) VALUES (?, ?)",
            (codigo, sexo),
        )
        return cursor.lastrowid


def criarProntuario(nomePaciente, nomePai, nomeMae, dataNascimento, sexo, cns, caixaId):
    """Cadastra um novo prontuário associado a uma caixa e retorna o ID gerado."""
    with conexao() as con:
        cursor = con.execute(
            """
            INSERT INTO prontuarios_antigos (
                nome_paciente, nome_pai, nome_mae, data_nascimento, sexo, CNS, caixasId
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (nomePaciente, nomePai, nomeMae, dataNascimento, sexo, cns, caixaId),
        )
        return cursor.lastrowid


# ─── Auditoria / Logs ──────────────────────────────────────────────────────────


def registrarLog(tipo, nomePaciente, dataNascimento, caixaCodigo, caixaSexo, dataHora):
    """Registra uma ação de auditoria (REABERTO ou ARQUIVADO) na tabela de logs."""
    with conexao() as con:
        con.execute(
            """
            INSERT INTO log_acoes (tipo, nomePaciente, dataNascimento, caixaCodigo, caixaSexo, dataHora)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (tipo, nomePaciente, dataNascimento, caixaCodigo, caixaSexo, dataHora),
        )


def buscarLogs(tipo=None):
    """Retorna todos os registros de log, opcionalmente filtrados por tipo (REABERTO ou ARQUIVADO)."""
    with conexao() as con:
        if tipo:
            return con.execute(
                """
                SELECT id, tipo, nomePaciente, dataNascimento, caixaCodigo, caixaSexo, dataHora
                FROM log_acoes
                WHERE tipo = ?
                ORDER BY id DESC
                """,
                (tipo,),
            ).fetchall()
        return con.execute(
            """
            SELECT id, tipo, nomePaciente, dataNascimento, caixaCodigo, caixaSexo, dataHora
            FROM log_acoes
            ORDER BY id DESC
            """
        ).fetchall()
