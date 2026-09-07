import string
import customtkinter as ctk

from components.TemaAcessivel import TemaAcessivel
from database.Banco import buscarCaixasComProntuariosPaginado, contarCaixas


class TelaCaixas(ctk.CTkToplevel):
    """Tela genérica e reutilizável para consulta de caixas arquivísticas por sexo."""

    # Quantidade de caixas renderizadas por página
    caixasPorPagina = 6

    def __init__(self, master, sexo, titulo):
        super().__init__(master=master)
        self.sexo = sexo
        self.titulo = titulo

        # Filtros e controle de estado da paginação
        self.letraAtual = None
        self.offset = 0
        self.totalCaixas = 0
        self.carregando = False
        self.botoesLetra = {}

        self.title(titulo)
        self.geometry("1040x680")
        self.minsize(760, 520)

        # Garante que a janela abra na frente da janela principal e receba foco imediato
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        paleta = TemaAcessivel.obter()
        self.configure(fg_color=paleta["fundo"])

        self.rotuloTitulo = ctk.CTkLabel(
            self, text=titulo, font=("Arial", 20, "bold"), text_color=paleta["texto"]
        )
        self.rotuloTitulo.pack(pady=(20, 4))
        self.rotuloSubtitulo = ctk.CTkLabel(
            self,
            text="Consulte os prontuarios organizados por caixa.",
            text_color=paleta["placeholder"],
        )
        self.rotuloSubtitulo.pack(pady=(0, 12))

        self.criarMenuAlfabeto()
        self.areaCaixas = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.areaCaixas.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.frameBotaoMais = None

        self.atualizarContagem()
        self.carregarPagina()

        # Inscreve a janela para atualizar dinamicamente quando a paleta for alterada
        TemaAcessivel.registrarObservador(self.aplicarPaleta)
        self.protocol("WM_DELETE_WINDOW", self.aoFechar)

    def aoFechar(self):
        TemaAcessivel.removerObservador(self.aplicarPaleta)
        self.destroy()

    def aplicarPaleta(self):
        # Atualiza em tempo real as cores da tela de caixas
        paleta = TemaAcessivel.obter()
        self.configure(fg_color=paleta["fundo"])
        if hasattr(self, "rotuloTitulo"):
            self.rotuloTitulo.configure(text_color=paleta["texto"])
        if hasattr(self, "rotuloSubtitulo"):
            self.rotuloSubtitulo.configure(text_color=paleta["placeholder"])
        self.atualizarDestaqueLetra()
        if not self.carregando:
            self.offset = 0
            self.limparAreaCaixas()
            self.atualizarContagem()
            self.carregarPagina()

    def criarMenuAlfabeto(self):
        # Monta a barra de atalhos A-Z rolável horizontalmente para filtragem rápida por letra
        frame = ctk.CTkScrollableFrame(
            self, orientation="horizontal", height=46, fg_color="transparent"
        )
        frame.pack(fill="x", padx=20, pady=(0, 12))
        paleta = TemaAcessivel.obter()
        botaoTodas = ctk.CTkButton(
            frame, text="Todas", width=64, height=32,
            fg_color=paleta["destaque"], hover_color=paleta["hover"],
            text_color=paleta["texto_destaque"],
            command=lambda: self.filtrarPorLetra(None),
        )
        botaoTodas.pack(side="left", padx=(0, 5))
        self.botoesLetra[None] = botaoTodas

        for letra in string.ascii_uppercase:
            botao = ctk.CTkButton(
                frame, text=letra, width=36, height=32,
                fg_color=paleta["barra"], hover_color=paleta["hover"],
                text_color=paleta["texto_barra"],
                command=lambda letraAtual=letra: self.filtrarPorLetra(letraAtual),
            )
            botao.pack(side="left", padx=2)
            self.botoesLetra[letra] = botao

    def atualizarDestaqueLetra(self):
        # Altera visualmente a cor do botão da letra selecionada no momento
        paleta = TemaAcessivel.obter()
        for chave, botao in self.botoesLetra.items():
            if chave == self.letraAtual:
                botao.configure(fg_color=paleta["destaque"], text_color=paleta["texto_destaque"])
            else:
                botao.configure(fg_color=paleta["barra"], text_color=paleta["texto_barra"])

    def filtrarPorLetra(self, letra):
        # Evita execuções simultâneas se já houver uma página sendo carregada
        if self.carregando:
            return
        self.letraAtual = letra
        self.offset = 0
        self.atualizarDestaqueLetra()
        self.limparAreaCaixas()
        self.atualizarContagem()
        self.carregarPagina()

    def limparAreaCaixas(self):
        # Destrói os cartões visuais para recarregar o novo filtro sem vazamento de memória
        for widget in self.areaCaixas.winfo_children():
            widget.destroy()
        self.frameBotaoMais = None

    def atualizarContagem(self):
        self.totalCaixas = contarCaixas(self.sexo, self.letraAtual)

    def carregarPagina(self):
        # Bloqueia reentrância na busca paginada
        if self.carregando:
            return
        self.carregando = True

        if self.frameBotaoMais:
            self.frameBotaoMais.destroy()
            self.frameBotaoMais = None

        paleta = TemaAcessivel.obter()
        if self.offset == 0 and self.totalCaixas == 0:
            descricao = "para a letra selecionada" if self.letraAtual else "cadastrada"
            ctk.CTkLabel(
                self.areaCaixas,
                text=f"Nenhuma caixa {self.sexo.lower()} {descricao}.",
                text_color=paleta["texto"],
            ).pack(pady=20)
            self.carregando = False
            return

        caixas = buscarCaixasComProntuariosPaginado(
            self.sexo, self.letraAtual, self.caixasPorPagina, self.offset
        )

        if not caixas:
            self.carregando = False
            return

        if self.offset == 0:
            for coluna in range(2):
                self.areaCaixas.grid_columnconfigure(coluna, weight=1)

        self.renderizarCaixasIncrementalmente(caixas, 0)

    def renderizarCaixasIncrementalmente(self, caixas, indice):
        # Renderiza cada cartão em ciclos de idle (after_idle) para manter a interface fluida sem congelar
        if indice >= len(caixas):
            self.offset += len(caixas)
            self.mostrarBotaoCarregarMais()
            self.carregando = False
            return

        caixa = caixas[indice]
        indiceGlobal = self.offset + indice
        self.criarCartaoCaixa(caixa, indiceGlobal)

        self.after_idle(
            lambda: self.renderizarCaixasIncrementalmente(caixas, indice + 1)
        )

    def mostrarBotaoCarregarMais(self):
        # Exibe a contagem de itens restantes e a opção de carregar o próximo lote
        restantes = self.totalCaixas - self.offset
        paleta = TemaAcessivel.obter()
        self.frameBotaoMais = ctk.CTkFrame(self.areaCaixas, fg_color="transparent")
        self.frameBotaoMais.grid(
            row=(self.offset // 2) + 1, column=0, columnspan=2,
            sticky="ew", pady=(10, 5),
        )

        if restantes <= 0:
            ctk.CTkLabel(
                self.frameBotaoMais,
                text=f"Todas as {self.offset} caixas carregadas.",
                text_color=paleta["placeholder"],
            ).pack(pady=5)
            return

        ctk.CTkButton(
            self.frameBotaoMais,
            text=f"Carregar mais ({restantes} restantes)",
            fg_color=paleta["destaque"],
            hover_color=paleta["hover"],
            text_color=paleta["texto_destaque"],
            height=36,
            command=self.carregarPagina,
        ).pack(pady=5)

    def criarCartaoCaixa(self, caixa, indice):
        # Renderiza a caixa arquivística no formato de card de grade (2 colunas)
        paleta = TemaAcessivel.obter()
        cartao = ctk.CTkFrame(
            self.areaCaixas, fg_color=paleta["card"], border_color=paleta["borda"],
            border_width=1, corner_radius=10,
        )
        cartao.grid(row=indice // 2, column=indice % 2, sticky="new", padx=7, pady=7)
        prontuarios = caixa["prontuarios"]
        ctk.CTkLabel(
            cartao, text=f"Caixa {caixa['codigo']}", font=("Arial", 17, "bold"),
            text_color=paleta["destaque"], anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 1))
        ctk.CTkLabel(
            cartao, text=f"{len(prontuarios)} prontuario(s)", text_color=paleta["placeholder"],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 8))

        if not prontuarios:
            ctk.CTkLabel(
                cartao, text="Nenhum prontuario nesta caixa.", text_color=paleta["texto"],
            ).pack(anchor="w", padx=14, pady=(2, 14))
            return

        for prontuario in prontuarios:
            self.criarProntuario(cartao, prontuario)

    def criarProntuario(self, master, prontuario):
        # Exibe os dados reduzidos de um paciente dentro do card da caixa
        paleta = TemaAcessivel.obter()
        bloco = ctk.CTkFrame(master, fg_color=paleta["card_item"], corner_radius=7)
        bloco.pack(fill="x", padx=12, pady=(0, 9))
        ctk.CTkLabel(
            bloco, text=prontuario["nomePaciente"], font=("Arial", 14, "bold"),
            text_color=paleta["texto"], anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 4))
        self.criarLinha(bloco, "Pai", prontuario["nomePai"])
        self.criarLinha(bloco, "Mae", prontuario["nomeMae"])
        self.criarLinha(bloco, "CNS", prontuario["cns"])

    def criarLinha(self, master, rotulo, valor):
        paleta = TemaAcessivel.obter()
        texto = valor if valor else "Nao informado"
        ctk.CTkLabel(
            master, text=f"{rotulo}: {texto}", text_color=paleta["texto"],
            anchor="w", wraplength=430,
        ).pack(fill="x", padx=10, pady=1)

