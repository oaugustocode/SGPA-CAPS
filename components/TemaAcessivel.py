"""Gerenciador central de paletas de acessibilidade e alto contraste para daltonismo."""


class TemaAcessivel:
    # Perfil ativo na interface (Padrão, Protanopia, Deuteranopia ou Tritanopia)
    perfilAtual = "Padrão"

    # Mapeamento de cores otimizadas para acessibilidade visual.
    # As combinações evitam confusão vermelho/verde (protanopia/deuteranopia) e azul/amarelo (tritanopia).
    paletas = {
        "Padrão": {
            "fundo": ("#F8FAFC", "#000814"),
            "barra": "#001D3D",
            "hover": "#003566",
            "borda": "#003566",
            "destaque": "#FFB703",
            "texto": "#FFFFFF",
            "placeholder": "#8D99AE",
        },
        "Protanopia": {
            "fundo": ("#F5F9FC", "#081A2B"),
            "barra": "#0072B2",
            "hover": "#005A8D",
            "borda": "#56B4E9",
            "destaque": "#F0E442",
            "texto": "#FFFFFF",
            "placeholder": "#B9DDF0",
        },
        "Deuteranopia": {
            "fundo": ("#FFF9ED", "#211B0E"),
            "barra": "#0072B2",
            "hover": "#005A8D",
            "borda": "#E69F00",
            "destaque": "#F0E442",
            "texto": "#FFFFFF",
            "placeholder": "#C8E5F4",
        },
        "Tritanopia": {
            "fundo": ("#FCF8FA", "#1B1017"),
            "barra": "#5B1A45",
            "hover": "#7A285F",
            "borda": "#CC79A7",
            "destaque": "#E69F00",
            "texto": "#FFFFFF",
            "placeholder": "#E8BED5",
        },
    }

    @classmethod
    def obter(cls):
        # Retorna o dicionário de cores referente ao perfil selecionado no momento
        return cls.paletas[cls.perfilAtual]

    @classmethod
    def selecionar(cls, perfil):
        # Atualiza o perfil ativo e retorna a nova paleta aplicada
        cls.perfilAtual = perfil
        return cls.obter()

