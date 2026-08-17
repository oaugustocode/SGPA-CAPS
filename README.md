# SGPA-CAPS - Sistema de Gestão de Prontuários Antigos

O **SGPA-CAPS** é uma aplicação desktop desenvolvida para a organização, consulta e gerenciamento de acervos físicos de prontuários antigos do Centro de Atenção Psicossocial (CAPS). O sistema foi idealizado para otimizar a localização de documentos arquivísticos, permitindo o agrupamento por caixas físicas numeradas, a busca rápida de pacientes por nome ou Cartão Nacional de Saúde (CNS), e o cadastro ágil de novos registros.

Além da gestão funcional de acervos, o projeto prioriza a acessibilidade visual, integrando modos de alto contraste adaptados para diferentes tipos de daltonismo.

> **Privacidade:** todos os nomes, filiações e números de CNS presentes no banco incluído neste repositório são dados sintéticos, gerados exclusivamente para demonstração. O projeto não contém dados reais de pacientes.

---

## Funcionalidades Principais

- **Pesquisa Instantânea com Autocompletar**: Campo de busca inteligente com filtro por nome do paciente ou número do CNS, equipado com técnica de *debounce* (180ms) para otimizar as consultas e evitar chamadas excessivas ao banco de dados.
- **Organização por Caixas Arquivísticas**: Divisão e visualização estruturada dos prontuários em caixas físicas categorizadas por sexo (Masculino e Feminino), limitadas a 20 prontuários por caixa para garantir legibilidade e controle de acervo.
- **Navegação Paginada e Filtro Alfabético**: Suporte à navegação por páginas e filtragem direta de caixas pela letra inicial do código ou dos prontuários contidos.
- **Cadastro de Prontuários e Caixas**: Formulário integrado para adição de novos prontuários de pacientes (nome, filiação, sexo, CNS) com opção de associação a uma caixa existente ou criação dinâmica de uma nova caixa física.
- **Exclusão Segura de Prontuários**: Fluxo de remoção por caixa, com seleção explícita do prontuário e confirmação antes da exclusão permanente.
- **Acessibilidade Visual (Suporte a Daltonismo)**: Alternância de temas visuais em tempo real adaptados para visão padrão, Protanopia, Deuteranopia e Tritanopia.
- **Gerador de Massa de Dados (Seed)**: Módulo embutido para população autônoma do banco de dados com até 1.000 registros sintéticos baseados na distribuição estatística de nomes brasileiros.

---

## Tecnologias Utilizadas

- **Linguagem de Programação**: Python 3.10+
- **Interface Gráfica (GUI)**: CustomTkinter (framework moderno construído sobre o Tkinter)
- **Pacote de Ícones**: `ctkfontawesome` (integração de ícones vetoriais FontAwesome com suporte a temas)
- **Banco de Dados**: SQLite 3 (persistência local com suporte a chaves estrangeiras e *Window Functions*)
- **Gerenciamento de Arquivos**: Módulo nativo `pathlib`

---

## Arquitetura e Funcionamento do Sistema

O sistema adota uma arquitetura modular em camadas, separando responsabilidades entre interface visual, lógica de componentes e persistência de dados.

1. **Camada de Apresentação (`views`)**:
   - `TelaPrincipal`: Ponto central de interação do usuário, contendo a barra de navegação superior e o motor de busca instantânea.
   - `TelaCaixas`, `TelaCaixasMasc`, `TelaCaixasFem`: Telas responsáveis por listar o acervo de caixas arquivísticas de forma paginada e organizada.
   - `TelaAdicionarPront`: Modal de formulário com validações para inserção de dados de pacientes e gerenciamento de caixas.
   - `TelaExcluirPront`: Modal de exclusão segura que lista somente os prontuários da caixa selecionada.
   - `TelaAcessbi`: Interface para seleção dos perfis de acessibilidade e ajuste dinâmico das paletas de cor.
   - `TelaAjuda`: Modal com instruções gerais de operação do sistema.

2. **Camada de Componentes (`components`)**:
   - `TemaAcessivel`: Classe gerenciadora que centraliza a definição de cores e estilos para a aplicação, permitindo a troca dinâmica de paletas entre as views sem necessidade de reinicialização.

3. **Camada de Dados (`database`)**:
   - `Banco.py`: Centraliza operações SQL, incluindo consultas parametrizadas, paginação, inserções e exclusões.
   - `Seed.py`: Script de geração de dados sintéticos para simulação de acervo.

---

## Estrutura do Projeto

```text
SGPA-CAPS/
├── components/
│   ├── TemaAcessivel.py        # Gerenciamento de temas e acessibilidade visual
│   └── __init__.py
├── database/
│   ├── Banco.py                # Camada de persistência e consultas SQLite
│   ├── BancoSistemaArquivos.db # Arquivo de banco de dados SQLite
│   ├── Seed.py                 # Script para geração de dados sintéticos
│   └── __init__.py
├── views/
│   ├── TelaAcessbi.py          # Modal de configuração de acessibilidade
│   ├── TelaAdicionarPront.py    # Modal de cadastro de novos prontuários
│   ├── TelaExcluirPront.py     # Modal de exclusão segura de prontuários
│   ├── TelaAjuda.py            # Modal de ajuda e instruções
│   ├── TelaCaixas.py           # Componente base de listagem de caixas
│   ├── TelaCaixasFem.py        # Visão de caixas femininas
│   ├── TelaCaixasMasc.py       # Visão de caixas masculinas
│   ├── TelaPrincipal.py        # Interface principal e busca de pacientes
│   └── __init__.py
├── .gitignore                  # Regras de exclusão do Git
├── LICENSE                     # Licença MIT
├── main.py                     # Ponto de entrada da aplicação
├── requirements.txt            # Dependências Python do projeto
└── README.md                   # Documentação do repositório
```

---

## Pré-requisitos e Instalação

### Pré-requisitos

- Python 3.10 ou superior instalado no sistema.
- Gerenciador de pacotes `pip`.

### Instalação das Dependências

Para instalar as dependências necessárias para a execução da interface gráfica e dos ícones, execute no terminal:

```bash
pip install -r requirements.txt
```

---

## Como Executar o Projeto

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/oaugustocode/SGPA-CAPS.git
   cd SGPA-CAPS
   ```

2. **Executar a Aplicação**:
   ```bash
   python main.py
   ```

---

## Geração de Dados para Testes (Seed)

Caso deseje recriar a base de dados com registros fictícios para testes de desempenho e navegação, utilize o comando abaixo:

```bash
python -m database.Seed
```

Este comando recriará as tabelas e gerará automaticamente 1.000 prontuários fictícios distribuídos entre caixas masculinas e femininas.

> O comando apaga os registros existentes antes de gerar novamente a base de demonstração. Não o execute sobre uma base que contenha dados que devam ser preservados.

---

## Recursos de Acessibilidade Visual

O sistema contempla quatro perfis de cores acessíveis:

- **Padrão**: Paleta moderna em tons de azul escuro e amarelo de alto contraste.
- **Protanopia**: Ajustada para usuários com insensibilidade à luz vermelha.
- **Deuteranopia**: Adaptada para insensibilidade à luz verde.
- **Tritanopia**: Otimizada para insensibilidade à luz azul.

A alteração do perfil pode ser realizada a qualquer momento através do ícone de acessibilidade localizado na barra superior da aplicação.

---

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.
