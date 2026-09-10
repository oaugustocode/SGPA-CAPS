import customtkinter as ctk
from ctkfontawesome import icon_to_ctkimage

from database.Banco import buscarProntuario, sugerirProntuarios
from views.TelaAcessbi import TelaAcessbi
from views.TelaAjuda import TelaAjuda
from views.TelaCaixasFem import TelaCaixasFem
from views.TelaCaixasMasc import TelaCaixasMasc
from views.TelaArquivarPront import TelaArquivarPront
from views.TelaReabrirPront import TelaReabrirPront
from components.TemaAcessivel import TemaAcessivel


class TelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão de Prontuários Antigos")
        self.geometry("900x600")
        self.minsize(720, 500)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])

        # Estado interno da pesquisa e debounce
        self.timerPesquisa = None
        self.sugestoes = []
        self.prontuarioAtualId = None

        self.carregarIcones()
        self.criarBarraSuperior()
        self.criarAreaPesquisa()

        # Inscreve a tela principal para reagir a mudanças no tema acessível
        TemaAcessivel.registrarObservador(self.aplicarPaleta)

    def carregarIcones(self):
        # Carrega os ícones FontAwesome com a cor de destaque do tema ativo
        fill_light, fill_dark = TemaAcessivel.corIcone()
        self.iconeCaixaMasc = icon_to_ctkimage("box", fill=fill_light, dark_fill=fill_dark, scale_to_width=22)
        self.iconeCaixaFem = icon_to_ctkimage("box", fill=fill_light, dark_fill=fill_dark, scale_to_width=22)
        self.iconePlus = icon_to_ctkimage("plus", fill=fill_light, dark_fill=fill_dark, scale_to_width=20)
        self.iconeExcluir = icon_to_ctkimage("xmark", fill=fill_light, dark_fill=fill_dark, scale_to_width=20)
        self.iconeAcessibilidade = icon_to_ctkimage("universal-access", fill=fill_light, dark_fill=fill_dark, scale_to_width=24)
        self.iconeAjuda = icon_to_ctkimage("circle-info", fill=fill_light, dark_fill=fill_dark, scale_to_width=24)
        self.iconeLupa = icon_to_ctkimage("magnifying-glass", fill=fill_light, dark_fill=fill_dark, scale_to_width=20)

    def criarBarraSuperior(self):
        # Monta a barra de navegação principal no topo da tela
        paleta = TemaAcessivel.obter()
        self.barraSuperior = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=paleta["barra"])
        self.barraSuperior.pack(side="top", fill="x")
        self.barraSuperior.grid_propagate(False)

        self.botaoCaixaMasc = ctk.CTkButton(
            self.barraSuperior, text="Caixa Masculina", image=self.iconeCaixaMasc,
            compound="left", fg_color="transparent", hover_color=paleta["hover"],
            text_color=paleta["texto_barra"], command=self.abrirCaixasMasc,
        )
        self.botaoCaixaFem = ctk.CTkButton(
            self.barraSuperior, text="Caixa Feminina", image=self.iconeCaixaFem,
            compound="left", fg_color="transparent", hover_color=paleta["hover"],
            text_color=paleta["texto_barra"], command=self.abrirCaixasFem,
        )
        self.botaoAdicionar = ctk.CTkButton(
            self.barraSuperior, text="Arquivar Prontuário", image=self.iconePlus,
            compound="left", fg_color="transparent", hover_color=paleta["hover"],
            text_color=paleta["texto_barra"], command=self.abrirArquivarProntuario,
        )
        self.botaoExcluir = ctk.CTkButton(
            self.barraSuperior, text="Reabrir Prontuário", image=self.iconeExcluir,
            compound="left", fg_color="transparent", hover_color=paleta["hover"],
            text_color=paleta["texto_barra"], command=self.abrirReabrirProntuario,
        )
        self.botaoAcessibilidade = ctk.CTkButton(
            self.barraSuperior, text="", width=40, image=self.iconeAcessibilidade,
            fg_color="transparent", hover_color=paleta["hover"],
            command=self.abrirAcessibilidade,
        )
        self.botaoAjuda = ctk.CTkButton(
            self.barraSuperior, text="", width=40, image=self.iconeAjuda,
            fg_color="transparent", hover_color=paleta["hover"],
            command=self.abrirAjuda,
        )
        self.botoesNavegacao = (
            self.botaoCaixaMasc,
            self.botaoCaixaFem,
            self.botaoAdicionar,
            self.botaoExcluir,
            self.botaoAcessibilidade,
            self.botaoAjuda,
        )
        self.ajustarNavegacao(TelaAcessbi.escalaFonteAtual)

    def ajustarNavegacao(self, escala):
        """Reorganiza a barra para manter todas as ações visíveis em fontes maiores."""
        for botao in self.botoesNavegacao:
            botao.grid_forget()
        for coluna in range(7):
            self.barraSuperior.grid_columnconfigure(coluna, weight=0)

        if escala >= 1.2:
            self.barraSuperior.configure(height=112)
            self.barraSuperior.grid_columnconfigure(2, weight=1)
            self.botaoCaixaMasc.grid(row=0, column=0, sticky="w", padx=(8, 4), pady=(8, 4))
            self.botaoCaixaFem.grid(row=0, column=1, sticky="w", padx=4, pady=(8, 4))
            self.botaoAdicionar.grid(row=1, column=0, sticky="w", padx=(8, 4), pady=(4, 8))
            self.botaoExcluir.grid(row=1, column=1, sticky="w", padx=4, pady=(4, 8))
            self.botaoAcessibilidade.grid(row=0, column=3, sticky="e", padx=8, pady=(8, 4))
            self.botaoAjuda.grid(row=1, column=3, sticky="e", padx=8, pady=(4, 8))
            return

        self.barraSuperior.configure(height=60)
        self.barraSuperior.grid_columnconfigure(4, weight=1)
        self.botaoCaixaMasc.grid(row=0, column=0, sticky="w", padx=(8, 4), pady=11)
        self.botaoCaixaFem.grid(row=0, column=1, sticky="w", padx=4, pady=11)
        self.botaoAdicionar.grid(row=0, column=2, sticky="w", padx=4, pady=11)
        self.botaoExcluir.grid(row=0, column=3, sticky="w", padx=4, pady=11)
        self.botaoAcessibilidade.grid(row=0, column=5, sticky="e", padx=4, pady=11)
        self.botaoAjuda.grid(row=0, column=6, sticky="e", padx=(4, 8), pady=11)

    def criarAreaPesquisa(self):
        # Mantém a pesquisa em uma área própria abaixo da navegação, com rolagem quando necessário
        paleta = TemaAcessivel.obter()
        self.areaConteudo = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
        )
        self.areaConteudo.pack(fill="both", expand=True)

        self.frameCentral = ctk.CTkFrame(self.areaConteudo, fg_color="transparent")
        self.frameCentral.pack(padx=20, pady=(35, 25))

        self.containerBusca = ctk.CTkFrame(
            self.frameCentral, fg_color=paleta["card"],
            border_color=paleta["borda"], border_width=1, corner_radius=8
        )
        self.containerBusca.pack(fill="x")
        self.rotuloIconeLupa = ctk.CTkLabel(self.containerBusca, text="", image=self.iconeLupa)
        self.rotuloIconeLupa.pack(side="left", padx=(12, 5), pady=8)
        self.campoPesquisa = ctk.CTkEntry(
            self.containerBusca, placeholder_text="Procure por nome ou CNS do paciente",
            width=410, height=40, fg_color="transparent", border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"]
        )
        self.campoPesquisa.pack(side="left", padx=(0, 10), pady=2)

        # Associa os eventos de digitação (para debounce) e confirmação via tecla Enter
        self.campoPesquisa.bind("<KeyRelease>", self.aoDigitar)
        self.campoPesquisa.bind("<Return>", self.selecionarPrimeiro)

        self.listaSugestoes = ctk.CTkFrame(self.frameCentral, fg_color=paleta["card"], corner_radius=0)
        self.listaSugestoes.pack(fill="x", pady=(1, 0))
        self.resultado = ctk.CTkFrame(self.frameCentral, fg_color="transparent")
        self.resultado.pack(fill="x", pady=(18, 0))
        self.listaSugestoes.pack_forget()

    def aoDigitar(self, evento=None):
        # Reinicia o timer a cada tecla pressionada para aguardar a pausa na digitação (debounce de 180ms)
        if self.timerPesquisa:
            self.after_cancel(self.timerPesquisa)
        self.timerPesquisa = self.after(180, self.atualizarSugestoes)

    def atualizarSugestoes(self):
        # Consulta o banco de dados e preenche a lista de sugestões instantâneas
        texto = self.campoPesquisa.get().strip()
        self.limparSugestoes()
        self.limparResultado()
        if len(texto) < 2:
            return
        self.sugestoes = sugerirProntuarios(texto)
        if not self.sugestoes:
            self.mostrarMensagem("Prontuario nao encontrado, digite novamente ou consulte manualmente")
            return
        paleta = TemaAcessivel.obter()
        for prontuario in self.sugestoes:
            textoBotao = f'{prontuario["nomePaciente"]} | Nasc: {prontuario["dataNascimento"]} | CNS {prontuario["cns"]}'
            ctk.CTkButton(
                self.listaSugestoes, text=textoBotao, anchor="w",
                height=32, fg_color="transparent", hover_color=paleta["hover"],
                text_color=paleta["texto"],
                command=lambda prontuarioId=prontuario["id"]: self.mostrarProntuario(prontuarioId)
            ).pack(fill="x", padx=4, pady=1)
        self.listaSugestoes.pack(fill="x", pady=(1, 0))

    def selecionarPrimeiro(self, evento=None):
        # Pressionar Enter seleciona automaticamente o primeiro resultado da lista de sugestões
        if self.sugestoes:
            self.mostrarProntuario(self.sugestoes[0]["id"])

    def mostrarProntuario(self, prontuarioId):
        # Exibe o card com as informações detalhadas do prontuário selecionado
        prontuario = buscarProntuario(prontuarioId)
        self.limparSugestoes()
        self.limparResultado()
        if not prontuario:
            self.mostrarMensagem("Prontuario nao encontrado, digite novamente ou consulte manualmente")
            return
        self.prontuarioAtualId = prontuarioId
        self.campoPesquisa.delete(0, "end")
        self.campoPesquisa.insert(0, prontuario["nomePaciente"])
        self.resultado.pack(fill="x", pady=(18, 0))
        paleta = TemaAcessivel.obter()
        ctk.CTkLabel(
            self.resultado, text="Prontuário encontrado", font=("Arial", 15, "bold"),
            text_color=paleta["texto"]
        ).pack(pady=(0, 10))
        cartao = ctk.CTkFrame(
            self.resultado, fg_color=paleta["card"], border_color=paleta["borda"],
            border_width=1, corner_radius=10
        )
        cartao.pack(fill="x")
        self.campo(cartao, "Nome completo do paciente", prontuario["nomePaciente"], 0, 0, 3)
        self.campo(cartao, "Nome do pai", prontuario["nomePai"] or "Não informado", 1, 0)
        self.campo(cartao, "Nome da mãe", prontuario["nomeMae"] or "Não informado", 1, 1)
        self.campo(cartao, "Data de Nascimento", prontuario["dataNascimento"] or "Não informada", 2, 0)
        sexoFormatado = "Masculino" if prontuario["sexo"] == "M" else "Feminino" if prontuario["sexo"] == "F" else (prontuario["sexo"] or "Não informado")
        self.campo(cartao, "Sexo", sexoFormatado, 2, 1)
        self.campo(cartao, "CNS", str(prontuario["cns"]), 3, 0)
        caixa = f'{prontuario["caixaSexo"] or "Sem sexo"} • {prontuario["caixaCodigo"] or "Sem caixa"}'
        self.campo(cartao, "Caixa", caixa, 3, 1)

    def campo(self, master, rotulo, valor, linha, coluna, colspan=1):
        # Componente reutilizável para exibir cada rótulo e valor formatado no card
        paleta = TemaAcessivel.obter()
        bloco = ctk.CTkFrame(master, fg_color="transparent")
        bloco.grid(row=linha, column=coluna, columnspan=colspan, sticky="ew", padx=10, pady=7)
        ctk.CTkLabel(bloco, text=rotulo, anchor="w", font=("Arial", 16), text_color=paleta["texto"]).pack(fill="x")
        ctk.CTkLabel(
            bloco, text=valor, anchor="w", fg_color=paleta["card_item"],
            text_color=paleta["texto"], corner_radius=4, padx=10, height=30
        ).pack(fill="x", pady=(3, 0))
        for i in range(3):
            master.grid_columnconfigure(i, weight=1)

    def mostrarMensagem(self, texto):
        paleta = TemaAcessivel.obter()
        corAviso = paleta["destaque"] if isinstance(paleta["destaque"], str) else paleta["destaque"][0]
        ctk.CTkLabel(self.resultado, text=texto, text_color=corAviso, font=("Arial", 12)).pack(pady=8)
        self.resultado.pack(fill="x", pady=(8, 0))

    def limparSugestoes(self):
        # Destrói os widgets filhos para desalocar memória da lista de sugestões
        for widget in self.listaSugestoes.winfo_children():
            widget.destroy()
        self.listaSugestoes.pack_forget()

    def limparResultado(self):
        # Remove a exibição anterior do prontuário
        self.prontuarioAtualId = None
        for widget in self.resultado.winfo_children():
            widget.destroy()
        self.resultado.pack_forget()

    # Métodos de navegação entre as telas do sistema com garantia de foco e primeiro plano
    def abrirAjuda(self): return self.abrir(TelaAjuda)
    def abrirCaixasMasc(self): return self.abrir(TelaCaixasMasc)
    def abrirCaixasFem(self): return self.abrir(TelaCaixasFem)
    def abrirAcessibilidade(self): return self.abrir(TelaAcessbi)
    def abrirArquivarProntuario(self): return self.abrir(TelaArquivarPront)
    def abrirReabrirProntuario(self): return self.abrir(TelaReabrirPront)

    def abrir(self, tela):
        janela = tela(master=self)
        janela.lift()
        janela.focus_force()
        return janela

    def aplicarPaleta(self):
        # Atualiza dinamicamente as cores e ícones da tela principal ao alterar o tema acessível
        paleta = TemaAcessivel.obter()
        self.configure(fg_color=paleta["fundo"])
        self.barraSuperior.configure(fg_color=paleta["barra"])

        # Recarrega os ícones com a cor de destaque da nova paleta
        self.carregarIcones()

        # Atualiza botões da barra superior (ícones, hover e cor de texto)
        self.botaoCaixaMasc.configure(image=self.iconeCaixaMasc, hover_color=paleta["hover"], text_color=paleta["texto_barra"])
        self.botaoCaixaFem.configure(image=self.iconeCaixaFem, hover_color=paleta["hover"], text_color=paleta["texto_barra"])
        self.botaoAdicionar.configure(image=self.iconePlus, hover_color=paleta["hover"], text_color=paleta["texto_barra"])
        self.botaoExcluir.configure(image=self.iconeExcluir, hover_color=paleta["hover"], text_color=paleta["texto_barra"])
        self.botaoAcessibilidade.configure(image=self.iconeAcessibilidade, hover_color=paleta["hover"])
        self.botaoAjuda.configure(image=self.iconeAjuda, hover_color=paleta["hover"])

        # Atualiza container e campo de busca
        self.areaConteudo.configure(fg_color="transparent")
        self.containerBusca.configure(fg_color=paleta["card"], border_color=paleta["borda"])
        if hasattr(self, "rotuloIconeLupa"):
            self.rotuloIconeLupa.configure(image=self.iconeLupa)
        self.campoPesquisa.configure(text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"])
        self.listaSugestoes.configure(fg_color=paleta["card"])

        # Re-renderiza o prontuário caso esteja sendo exibido para atualizar cores e bordas
        if self.prontuarioAtualId:
            self.mostrarProntuario(self.prontuarioAtualId)
