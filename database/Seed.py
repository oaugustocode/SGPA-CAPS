"""Geração autônoma de dados fictícios para testes e simulação do SGDA-CAPS.

Para recriar o banco de teste com 1.000 prontuários, execute:
    python -m database.Seed
"""

from __future__ import annotations
from collections import defaultdict
import datetime
from pathlib import Path
import random
import sys

# Garante que a pasta raiz do projeto esteja no sys.path para execução direta
caminhoRaiz = str(Path(__file__).resolve().parent.parent)
if caminhoRaiz not in sys.path:
    sys.path.insert(0, caminhoRaiz)

from database.Banco import conexao

# ─── Configurações e pesos de geração ───────────────────────────────────────────

# Define a semente fixa (42) para garantir reprodutibilidade nos dados gerados
gerador = random.Random(42)
totalPorSexo = 500
probabilidadePaiNaoDeclarado = 0.12
limiteProntuariosPorCaixa = 20

# Distribuição percentual aproximada por letra inicial de nomes no Brasil
pesosIniciais = [
    ("A", 14), ("B", 4), ("C", 11), ("D", 6), ("E", 4), ("F", 4), ("G", 4), ("H", 2),
    ("I", 2), ("J", 9), ("K", 1), ("L", 7), ("M", 10), ("N", 5), ("O", 2), ("P", 8),
    ("Q", 1), ("R", 7), ("S", 9), ("T", 6), ("U", 1), ("V", 5), ("W", 1), ("X", 1),
    ("Y", 1), ("Z", 1)
]

nomesMasculinos = [
    "Adriano", "Afonso", "Alan", "Alberto", "Alexandre", "Alisson", "Andre", "Antonio", "Arthur", "Augusto",
    "Bernardo", "Breno", "Bruno", "Caio", "Carlos", "Cesar", "Claudio", "Cristian", "Daniel", "Danilo",
    "Davi", "Diego", "Douglas", "Eduardo", "Elias", "Emerson", "Eric", "Fabio", "Fabricio", "Felipe",
    "Fernando", "Flavio", "Gabriel", "Geraldo", "Gilberto", "Guilherme", "Gustavo", "Henrique", "Hugo", "Igor",
    "Ivan", "Jefferson", "Joao", "Jonathan", "Juliano", "Junior", "Kevin", "Kelvin", "Kleber", "Leandro",
    "Leonardo", "Lucas", "Luiz", "Marcelo", "Marcos", "Mateus", "Matheus", "Mauricio", "Miguel", "Nicolas",
    "Nelson", "Nilton", "Otavio", "Osmar", "Paulo", "Patrick", "Pedro", "Quirino", "Rafael", "Renato",
    "Ricardo", "Rodrigo", "Rogerio", "Samuel", "Sandro", "Sergio", "Silvio", "Tadeu", "Thiago", "Tiago",
    "Tomas", "Ubiratan", "Vinicius", "Victor", "Vitor", "Wagner", "Wallace", "Wesley", "Xavier", "Yuri",
    "Yan", "Zeca", "Zeferino"
]

nomesFemininos = [
    "Adriana", "Aline", "Alessandra", "Alice", "Amanda", "Ana", "Angela", "Ariane", "Barbara", "Beatriz",
    "Bianca", "Bruna", "Camila", "Carla", "Cintia", "Claudia", "Cristiane", "Daniela", "Daiane", "Debora",
    "Diana", "Eduarda", "Elaine", "Eliane", "Eloisa", "Erika", "Fabiana", "Fatima", "Fernanda", "Flavia",
    "Francine", "Gabriela", "Geovana", "Giovana", "Gisele", "Glaucia", "Helena", "Heloisa", "Iara", "Ingrid",
    "Isabella", "Ivana", "Jacqueline", "Jessica", "Juliana", "Julia", "Josefa", "Karen", "Kamila", "Katia",
    "Kesia", "Larissa", "Leticia", "Livia", "Luana", "Marcia", "Mariana", "Mayara", "Melissa", "Michelle",
    "Monica", "Natalia", "Neide", "Nicole", "Noemia", "Odete", "Olivia", "Paloma", "Patricia", "Paula",
    "Priscila", "Quezia", "Rafaela", "Renata", "Roberta", "Rosana", "Rose", "Sabrina", "Samara", "Silvana",
    "Simone", "Sonia", "Tatiane", "Talita", "Tania", "Thais", "Ursula", "Vanessa", "Vitoria", "Viviane",
    "Walquiria", "Wanderlea", "Xenia", "Ximena", "Yasmin", "Yara", "Yohana", "Zelia", "Zilda", "Zuleica"
]

sobrenomes = [
    "Almeida", "Alves", "Andrade", "Araujo", "Azevedo", "Barbosa", "Barros", "Batista", "Campos", "Cardoso",
    "Carvalho", "Costa", "Cruz", "Cunha", "Dantas", "Dias", "Farias", "Ferreira", "Fonseca", "Freitas",
    "Garcia", "Gomes", "Goncalves", "Guimaraes", "Lima", "Lopes", "Machado", "Marques", "Martins", "Mendes",
    "Moraes", "Moreira", "Nogueira", "Oliveira", "Pacheco", "Paiva", "Pereira", "Pinto", "Ramos", "Reis",
    "Ribeiro", "Rocha", "Rodrigues", "Santos", "Silva", "Souza", "Teixeira", "Vieira", "Xavier"
]


# ─── Funções internas de geração ───────────────────────────────────────────────

def _gruposPorInicial(nomes):
    # Agrupa nomes próprios pela primeira letra para sorteio consistente
    grupos = defaultdict(list)
    for nome in nomes:
        grupos[nome[0].upper()].append(nome)
    return grupos


def _escolherPrimeiroNome(grupos, letra):
    opcoes = grupos.get(letra)
    if opcoes:
        return gerador.choice(opcoes)
    todos = []
    for lista in grupos.values():
        todos.extend(lista)
    return gerador.choice(todos)


def _escolherLetra():
    letras = [letra for letra, _ in pesosIniciais]
    pesos = [peso for _, peso in pesosIniciais]
    return gerador.choices(letras, weights=pesos, k=1)[0]


def _gerarNomeCompleto(gruposPrimeiroNome):
    letra = _escolherLetra()
    primeiro = _escolherPrimeiroNome(gruposPrimeiroNome, letra)
    amostraSobrenomes = gerador.sample(sobrenomes, 2)
    return f"{primeiro} {amostraSobrenomes[0]} {amostraSobrenomes[1]}", letra


def _gerarNomeFamiliar(gruposPrimeiroNome):
    primeiro = _escolherPrimeiroNome(gruposPrimeiroNome, _escolherLetra())
    amostraSobrenomes = gerador.sample(sobrenomes, 1)
    return f"{primeiro} {amostraSobrenomes[0]}"


def _gerarCnsUnico(usados):
    # Gera um CNS fictício único com exatamente 5 dígitos
    while True:
        cns = f"{gerador.randint(10000, 99999):05d}"
        if cns not in usados:
            usados.add(cns)
            return cns


def _gerarDataNascimento():
    # Gera datas para crianças e adolescentes de 0 a 17 anos e 11 meses (estritamente < 18 anos)
    hoje = datetime.date.today()
    # Idade em dias entre 15 dias e 17 anos + 330 dias
    dias = gerador.randint(15, 17 * 365 + 330)
    nascimento = hoje - datetime.timedelta(days=dias)
    return nascimento.strftime("%d/%m/%Y")


def _quantidadeCaixasPorLetra(total):
    # Dimensiona o número de caixas necessárias conforme o volume de prontuários da letra
    if total >= 70:
        return 4
    if total >= 35:
        return 3
    if total >= 12:
        return 2
    return 1


def _gerarProntuarios(sexo, total):
    nomesBase = nomesMasculinos if sexo == "M" else nomesFemininos
    gruposPrimeiroNome = _gruposPorInicial(nomesBase)
    gruposMae = _gruposPorInicial(nomesFemininos)
    gruposPai = _gruposPorInicial(nomesMasculinos)
    usadosCns = set()
    registros = []

    for _ in range(total):
        nomePaciente, letra = _gerarNomeCompleto(gruposPrimeiroNome)
        nomeMae = _gerarNomeFamiliar(gruposMae)
        nomePai = (
            "Nao declarado"
            if gerador.random() < probabilidadePaiNaoDeclarado
            else _gerarNomeFamiliar(gruposPai)
        )
        registros.append(
            {
                "sexo": sexo,
                "nomePaciente": nomePaciente,
                "nomePai": nomePai,
                "nomeMae": nomeMae,
                "dataNascimento": _gerarDataNascimento(),
                "cns": _gerarCnsUnico(usadosCns),
                "letra": letra,
            }
        )

    return registros


def _distribuirCaixas(registros, rotuloSexo):
    # Distribui os prontuários alfabeticamente entre as caixas criadas
    porLetra = defaultdict(list)
    for registro in registros:
        porLetra[registro["letra"]].append(registro)

    caixas = []
    prontuarios = []

    for letra in sorted(porLetra):
        grupo = sorted(porLetra[letra], key=lambda item: item["nomePaciente"])
        quantidade = _quantidadeCaixasPorLetra(len(grupo))
        codigos = [f"{letra}{indice}" for indice in range(1, quantidade + 1)]

        for codigo in codigos:
            caixas.append({"codigo": codigo, "sexo": rotuloSexo})

        for indice, registro in enumerate(grupo):
            codigo = codigos[indice % len(codigos)]
            prontuarios.append(
                {
                    "nomePaciente": registro["nomePaciente"],
                    "nomePai": registro["nomePai"],
                    "nomeMae": registro["nomeMae"],
                    "dataNascimento": registro["dataNascimento"],
                    "sexo": registro["sexo"],
                    "cns": registro["cns"],
                    "caixaCodigo": codigo,
                    "caixaSexo": rotuloSexo,
                }
            )

    return caixas, prontuarios


def _criarEsquema(con):
    # Recria as tabelas e índices zerando a base anterior
    con.executescript(
        """
        DROP TABLE IF EXISTS prontuarios_antigos;
        DROP TABLE IF EXISTS caixas;

        CREATE TABLE caixas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            sexo TEXT NOT NULL CHECK (sexo IN ('Masculino', 'Feminino')),
            UNIQUE (sexo, codigo)
        );

        CREATE TABLE prontuarios_antigos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_paciente TEXT NOT NULL,
            nome_pai TEXT,
            nome_mae TEXT,
            data_nascimento TEXT NOT NULL,
            sexo TEXT NOT NULL CHECK (sexo IN ('M', 'F')),
            CNS TEXT NOT NULL CHECK (length(CNS) = 5 AND CNS NOT GLOB '*[^0-9]*'),
            caixasId INTEGER NOT NULL,
            FOREIGN KEY(caixasId) REFERENCES caixas(id)
        );

        CREATE INDEX IF NOT EXISTS idx_prontuarios_nome_paciente
            ON prontuarios_antigos(nome_paciente COLLATE NOCASE);

        CREATE INDEX IF NOT EXISTS idx_prontuarios_data_nascimento
            ON prontuarios_antigos(data_nascimento);

        CREATE INDEX IF NOT EXISTS idx_prontuarios_cns
            ON prontuarios_antigos(CNS);

        CREATE INDEX IF NOT EXISTS idx_prontuarios_caixas_id
            ON prontuarios_antigos(caixasId);

        CREATE INDEX IF NOT EXISTS idx_caixas_sexo
            ON caixas(sexo);

        CREATE INDEX IF NOT EXISTS idx_caixas_codigo
            ON caixas(codigo);
        """
    )


# ─── Função principal ──────────────────────────────────────────────────────────

def recriarBancoDeTeste():
    # Ponto de entrada para popular o banco de desenvolvimento
    masculinos = _gerarProntuarios("M", totalPorSexo)
    femininos = _gerarProntuarios("F", totalPorSexo)

    caixasMasc, prontuariosMasc = _distribuirCaixas(masculinos, "Masculino")
    caixasFem, prontuariosFem = _distribuirCaixas(femininos, "Feminino")

    with conexao() as con:
        _criarEsquema(con)
        con.executemany(
            "INSERT INTO caixas (codigo, sexo) VALUES (?, ?)",
            [(caixa["codigo"], caixa["sexo"]) for caixa in caixasMasc + caixasFem],
        )

        mapeamentoCaixas = {
            (linha["codigo"], linha["sexo"]): linha["id"]
            for linha in con.execute("SELECT id, codigo, sexo FROM caixas").fetchall()
        }

        con.executemany(
            """
            INSERT INTO prontuarios_antigos (
                nome_paciente, nome_pai, nome_mae, data_nascimento, sexo, CNS, caixasId
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    prontuario["nomePaciente"],
                    prontuario["nomePai"],
                    prontuario["nomeMae"],
                    prontuario["dataNascimento"],
                    prontuario["sexo"],
                    prontuario["cns"],
                    mapeamentoCaixas[(prontuario["caixaCodigo"], prontuario["caixaSexo"])],
                )
                for prontuario in prontuariosMasc + prontuariosFem
            ],
        )

    print("Banco recriado com sucesso.")
    print(f"Prontuarios: {len(prontuariosMasc) + len(prontuariosFem)}")
    print(f"Caixas: {len(caixasMasc) + len(caixasFem)}")


if __name__ == "__main__":
    recriarBancoDeTeste()

