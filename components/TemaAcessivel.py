"""Gerenciador central de paletas de acessibilidade e alto contraste para daltonismo."""


class TemaAcessivel:
    # Perfil ativo na interface (Padrão, Protanopia, Deuteranopia ou Tritanopia)
    perfilAtual = "Padrão"
    _observadores = []

    # Mapeamento de cores otimizadas para acessibilidade visual e daltonismo.
    # Baseado no padrão internacional Okabe-Ito / Color Universal Design (CUD) e diretrizes WCAG.
    # Cada chave suporta tupla (modo_claro, modo_escuro) para perfeita harmonia visual.
    paletas = {
        "Padrão": {
            "fundo": ("#F8FAFC", "#000814"),
            "barra": ("#001D3D", "#001D3D"),
            "card": ("#FFFFFF", "#001428"),
            "card_item": ("#F1F5F9", "#002855"),
            "hover": ("#003566", "#003566"),
            "borda": ("#CBD5E1", "#003566"),
            "destaque": ("#D97706", "#FFB703"),
            "texto": ("#0F172A", "#FFFFFF"),
            "texto_barra": ("#FFFFFF", "#FFFFFF"),
            "texto_destaque": ("#000814", "#000814"),
            "placeholder": ("#64748B", "#8D99AE"),
        },
        "Protanopia": {
            # Deficiência no cone vermelho (L-cone).
            # Evita distinções vermelho/verde; prioriza azuis profundos, azul celeste e amarelo puro com alta luminância.
            "fundo": ("#F4F8FC", "#081626"),
            "barra": ("#004B87", "#003057"),
            "card": ("#FFFFFF", "#0D223A"),
            "card_item": ("#E1EDF8", "#143354"),
            "hover": ("#005FA8", "#005FA8"),
            "borda": ("#56B4E9", "#56B4E9"),
            "destaque": ("#0072B2", "#F0E442"),
            "texto": ("#071829", "#FFFFFF"),
            "texto_barra": ("#FFFFFF", "#FFFFFF"),
            "texto_destaque": ("#FFFFFF", "#081626"),
            "placeholder": ("#4A6B8A", "#9EC8E6"),
        },
        "Deuteranopia": {
            # Deficiência no cone verde (M-cone) - forma mais frequente de daltonismo.
            # Evita confusão verde/vermelho; prioriza azul royal (#0072B2), amarelo dourado (#E69F00) e alto contraste.
            "fundo": ("#FBF9F5", "#12171E"),
            "barra": ("#005A9E", "#0B2238"),
            "card": ("#FFFFFF", "#142A42"),
            "card_item": ("#F0EAE1", "#1B3958"),
            "hover": ("#0070C0", "#0E4877"),
            "borda": ("#D55E00", "#E69F00"),
            "destaque": ("#D55E00", "#E69F00"),
            "texto": ("#101720", "#FFFFFF"),
            "texto_barra": ("#FFFFFF", "#FFFFFF"),
            "texto_destaque": ("#FFFFFF", "#12171E"),
            "placeholder": ("#576675", "#A8BCCD"),
        },
        "Tritanopia": {
            # Deficiência no cone azul (S-cone).
            # Evita contraste azul/amarelo; emprega Carmesim/Rosa avermelhado (#CC79A7), Grafite e Turquesa de alto contraste.
            "fundo": ("#FCF7F9", "#1A1017"),
            "barra": ("#4A122E", "#380B20"),
            "card": ("#FFFFFF", "#2A1322"),
            "card_item": ("#F5E6EE", "#3D1D32"),
            "hover": ("#6B1C44", "#5E183B"),
            "borda": ("#CC79A7", "#CC79A7"),
            "destaque": ("#990033", "#CC79A7"),
            "texto": ("#1C0E17", "#FFFFFF"),
            "texto_barra": ("#FFFFFF", "#FFFFFF"),
            "texto_destaque": ("#FFFFFF", "#1A1017"),
            "placeholder": ("#6D5262", "#D2B7C6"),
        },
    }

    @classmethod
    def obter(cls):
        # Retorna o dicionário de cores referente ao perfil selecionado no momento
        return cls.paletas[cls.perfilAtual]

    @classmethod
    def corIcone(cls):
        # Retorna tupla (cor_clara, cor_escura) para preenchimento de ícones FontAwesome
        destaque = cls.obter()["destaque"]
        if isinstance(destaque, tuple):
            return destaque[0], destaque[1]
        return destaque, destaque

    @classmethod
    def selecionar(cls, perfil):
        # Atualiza o perfil ativo e notifica observadores cadastrados
        if perfil in cls.paletas:
            cls.perfilAtual = perfil
            cls.notificarObservadores()
        return cls.obter()

    @classmethod
    def registrarObservador(cls, callback):
        # Registra um callback para ser acionado quando a paleta for alterada
        if callback not in cls._observadores:
            cls._observadores.append(callback)

    @classmethod
    def removerObservador(cls, callback):
        # Remove o callback para evitar vazamentos de memória ao fechar janelas
        if callback in cls._observadores:
            cls._observadores.remove(callback)

    @classmethod
    def notificarObservadores(cls):
        # Executa todos os callbacks registrados na troca de perfil
        for observador in list(cls._observadores):
            try:
                observador()
            except Exception:
                pass


