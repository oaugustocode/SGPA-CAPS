import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel
from database.Banco import listarCaixas, criarCaixa, criarProntuario


class TelaAdicionarPront(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Adicionar Prontuário")
        self.geometry("900x680")
        self.minsize(720, 580)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.attributes("-topmost", True)

        self.cacheCaixas = []
        self.criarLayoutFormulario()

    # ─── Layout principal ──────────────────────────────────────────────────

    def criarLayoutFormulario(self):
        paleta = TemaAcessivel.obter()

        # Título da janela modal
        ctk.CTkLabel(
            self, text="Adicionar Prontuário",
            font=("Arial", 20, "bold"),
            text_color=("#001D3D", "#FFFFFF"),
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self, text="Preencha os dados abaixo para cadastrar um novo prontuário.",
            text_color=paleta["placeholder"],
        ).pack(pady=(0, 16))

        # ── Seção: Formulário de cadastro do paciente ────────────────────────
        frameFormulario = ctk.CTkFrame(self, fg_color=paleta["barra"],
                                        border_color=paleta["borda"], border_width=1,
                                        corner_radius=10)
        frameFormulario.pack(fill="x", padx=30, pady=(0, 10))

        # Nome do Paciente (campo obrigatório em linha inteira)
        self._criarRotulo(frameFormulario, "Nome do Paciente *")
        self.entradaNome = ctk.CTkEntry(frameFormulario, placeholder_text="Nome completo do paciente",
                                         height=36, fg_color=paleta["hover"],
                                         border_width=0, text_color=paleta["texto"],
                                         placeholder_text_color=paleta["placeholder"])
        self.entradaNome.pack(fill="x", padx=16, pady=(0, 10))

        # Linha 2: Pai + Mãe alinhados em duas colunas de peso igual
        linhaPaiMae = ctk.CTkFrame(frameFormulario, fg_color="transparent")
        linhaPaiMae.pack(fill="x", padx=16, pady=(0, 10))
        linhaPaiMae.grid_columnconfigure(0, weight=1)
        linhaPaiMae.grid_columnconfigure(1, weight=1)

        blocoPai = ctk.CTkFrame(linhaPaiMae, fg_color="transparent")
        blocoPai.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoPai, "Nome do Pai", pack=False)
        self.entradaPai = ctk.CTkEntry(blocoPai, placeholder_text="Nome do pai",
                                        height=36, fg_color=paleta["hover"],
                                        border_width=0, text_color=paleta["texto"],
                                        placeholder_text_color=paleta["placeholder"])
        self.entradaPai.pack(fill="x")

        blocoMae = ctk.CTkFrame(linhaPaiMae, fg_color="transparent")
        blocoMae.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoMae, "Nome da Mãe", pack=False)
        self.entradaMae = ctk.CTkEntry(blocoMae, placeholder_text="Nome da mãe",
                                        height=36, fg_color=paleta["hover"],
                                        border_width=0, text_color=paleta["texto"],
                                        placeholder_text_color=paleta["placeholder"])
        self.entradaMae.pack(fill="x")

        # Linha 3: CNS (3/4 da largura) + Sexo (1/4 da largura)
        linhaCnsSexo = ctk.CTkFrame(frameFormulario, fg_color="transparent")
        linhaCnsSexo.pack(fill="x", padx=16, pady=(0, 10))
        linhaCnsSexo.grid_columnconfigure(0, weight=3)
        linhaCnsSexo.grid_columnconfigure(1, weight=1)

        blocoCns = ctk.CTkFrame(linhaCnsSexo, fg_color="transparent")
        blocoCns.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoCns, "CNS (15 dígitos) *", pack=False)
        self.entradaCns = ctk.CTkEntry(blocoCns, placeholder_text="000000000000000",
                                        height=36, fg_color=paleta["hover"],
                                        border_width=0, text_color=paleta["texto"],
                                        placeholder_text_color=paleta["placeholder"])
        self.entradaCns.pack(fill="x")

        blocoSexo = ctk.CTkFrame(linhaCnsSexo, fg_color="transparent")
        blocoSexo.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoSexo, "Sexo *", pack=False)
        self.opcaoSexo = ctk.CTkOptionMenu(blocoSexo, values=["M", "F"],
                                            height=36, width=100,
                                            fg_color=paleta["hover"],
                                            button_color=paleta["destaque"],
                                            button_hover_color=paleta["hover"])
        self.opcaoSexo.pack(fill="x")

        # Linha 4: Seleção de Caixa arquivística vinculada
        self._criarRotulo(frameFormulario, "Caixa *")
        self.opcaoCaixa = ctk.CTkOptionMenu(frameFormulario, values=["Carregando..."],
                                             height=36,
                                             fg_color=paleta["hover"],
                                             button_color=paleta["destaque"],
                                             button_hover_color=paleta["hover"])
        self.opcaoCaixa.pack(fill="x", padx=16, pady=(0, 14))

        # Botão para efetuar a gravação no banco
        ctk.CTkButton(frameFormulario, text="Salvar Prontuário",
                       height=40, corner_radius=8,
                       fg_color=paleta["destaque"],
                       hover_color=paleta["hover"],
                       text_color="#001D3D",
                       font=("Arial", 14, "bold"),
                       command=self.salvarProntuario).pack(pady=(0, 16))

        # Rótulo de feedback visual temporário (sucesso / erro)
        self.rotuloStatus = ctk.CTkLabel(frameFormulario, text="", height=20,
                                          text_color="#4ADE80")
        self.rotuloStatus.pack(pady=(0, 10))

        # ── Separador ─────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=2, fg_color=paleta["borda"]).pack(
            fill="x", padx=30, pady=(6, 10))

        # ── Seção: Cadastro rápido de nova caixa ───────────────────────────
        frameCaixa = ctk.CTkFrame(self, fg_color=paleta["barra"],
                                   border_color=paleta["borda"], border_width=1,
                                   corner_radius=10)
        frameCaixa.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(frameCaixa, text="Criar Nova Caixa",
                      font=("Arial", 16, "bold"),
                      text_color=paleta["destaque"]).pack(pady=(14, 8))

        linhaCaixa = ctk.CTkFrame(frameCaixa, fg_color="transparent")
        linhaCaixa.pack(fill="x", padx=16, pady=(0, 10))
        linhaCaixa.grid_columnconfigure(0, weight=2)
        linhaCaixa.grid_columnconfigure(1, weight=1)

        blocoCodigo = ctk.CTkFrame(linhaCaixa, fg_color="transparent")
        blocoCodigo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoCodigo, "Código da Caixa", pack=False)
        self.entradaCodigo = ctk.CTkEntry(blocoCodigo, placeholder_text="Ex: A1, B2...",
                                           height=36, fg_color=paleta["hover"],
                                           border_width=0, text_color=paleta["texto"],
                                           placeholder_text_color=paleta["placeholder"])
        self.entradaCodigo.pack(fill="x")

        blocoSexoCaixa = ctk.CTkFrame(linhaCaixa, fg_color="transparent")
        blocoSexoCaixa.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoSexoCaixa, "Sexo da Caixa", pack=False)
        self.opcaoSexoCaixa = ctk.CTkOptionMenu(blocoSexoCaixa,
                                                 values=["Masculino", "Feminino"],
                                                 height=36, width=140,
                                                 fg_color=paleta["hover"],
                                                 button_color=paleta["destaque"],
                                                 button_hover_color=paleta["hover"])
        self.opcaoSexoCaixa.pack(fill="x")

        ctk.CTkButton(frameCaixa, text="Criar Caixa",
                       height=36, corner_radius=8,
                       fg_color=paleta["destaque"],
                       hover_color=paleta["hover"],
                       text_color="#001D3D",
                       font=("Arial", 13, "bold"),
                       command=self.salvarCaixa).pack(pady=(4, 10))

        self.rotuloStatusCaixa = ctk.CTkLabel(frameCaixa, text="", height=20,
                                               text_color="#4ADE80")
        self.rotuloStatusCaixa.pack(pady=(0, 10))

        # Popula o menu de opções com as caixas cadastradas
        self.atualizarDropdownCaixas()

    # ─── Helpers ───────────────────────────────────────────────────────────

    def _criarRotulo(self, master, texto, pack=True):
        # Auxiliar estático para criar rótulos de campos com estilo uniforme
        paleta = TemaAcessivel.obter()
        label = ctk.CTkLabel(master, text=texto, anchor="w",
                              font=("Arial", 13),
                              text_color=paleta["texto"])
        if pack:
            label.pack(fill="x", padx=16, pady=(10, 2))
        else:
            label.pack(fill="x", pady=(0, 2))
        return label

    def atualizarDropdownCaixas(self):
        # Atualiza a lista em memória (cache) e recarrega os itens no OptionMenu
        self.cacheCaixas = listarCaixas()
        if self.cacheCaixas:
            opcoes = [
                f"{caixa['codigo']} — {caixa['sexo']}"
                for caixa in self.cacheCaixas
            ]
            self.opcaoCaixa.configure(values=opcoes)
            self.opcaoCaixa.set(opcoes[0])
        else:
            self.opcaoCaixa.configure(values=["Nenhuma caixa encontrada"])
            self.opcaoCaixa.set("Nenhuma caixa encontrada")

    def _mostrarFeedback(self, label, texto, cor):
        # Exibe uma mensagem de status temporária por 4 segundos
        label.configure(text=texto, text_color=cor)
        self.after(4000, lambda: label.configure(text=""))

    # ─── Ações ─────────────────────────────────────────────────────────────

    def salvarProntuario(self):
        # Coleta e higieniza os valores digitados nos campos
        nome = self.entradaNome.get().strip()
        pai = self.entradaPai.get().strip() or None
        mae = self.entradaMae.get().strip() or None
        cns = self.entradaCns.get().strip()
        sexo = self.opcaoSexo.get()

        # Validação do nome obrigatório
        if not nome:
            self._mostrarFeedback(self.rotuloStatus,
                                   "⚠ Nome do paciente é obrigatório.", "#EF4444")
            return

        # Validação estrita do padrão de 15 dígitos numéricos do CNS
        if not cns or len(cns) != 15 or not cns.isdigit():
            self._mostrarFeedback(self.rotuloStatus,
                                   "⚠ CNS deve ter exatamente 15 dígitos numéricos.", "#EF4444")
            return

        if not self.cacheCaixas:
            self._mostrarFeedback(self.rotuloStatus,
                                   "⚠ Nenhuma caixa disponível. Crie uma caixa primeiro.", "#EF4444")
            return

        # Identifica o ID da caixa selecionada a partir do texto formatado
        selecionado = self.opcaoCaixa.get()
        caixaId = None
        for caixa in self.cacheCaixas:
            texto = f"{caixa['codigo']} — {caixa['sexo']}"
            if texto == selecionado:
                caixaId = caixa["id"]
                break

        if caixaId is None:
            self._mostrarFeedback(self.rotuloStatus,
                                   "⚠ Selecione uma caixa válida.", "#EF4444")
            return

        try:
            criarProntuario(nome, pai, mae, sexo, cns, caixaId)
            self._mostrarFeedback(self.rotuloStatus,
                                   "✓ Prontuário salvo com sucesso!", "#4ADE80")
            # Reseta os campos após o salvamento bem-sucedido
            self.entradaNome.delete(0, "end")
            self.entradaPai.delete(0, "end")
            self.entradaMae.delete(0, "end")
            self.entradaCns.delete(0, "end")
        except Exception as e:
            self._mostrarFeedback(self.rotuloStatus,
                                   f"✗ Erro ao salvar: {e}", "#EF4444")

    def salvarCaixa(self):
        # Garante caixa alta para o código da caixa (ex: A1, B2)
        codigo = self.entradaCodigo.get().strip().upper()
        sexo = self.opcaoSexoCaixa.get()

        if not codigo:
            self._mostrarFeedback(self.rotuloStatusCaixa,
                                   "⚠ Código da caixa é obrigatório.", "#EF4444")
            return

        try:
            criarCaixa(codigo, sexo)
            self._mostrarFeedback(self.rotuloStatusCaixa,
                                   f"✓ Caixa {codigo} ({sexo}) criada!", "#4ADE80")
            self.entradaCodigo.delete(0, "end")
            self.atualizarDropdownCaixas()
        except Exception as e:
            msg = str(e)
            if "UNIQUE" in msg:
                self._mostrarFeedback(self.rotuloStatusCaixa,
                                       "⚠ Já existe uma caixa com este código e sexo.", "#EF4444")
            else:
                self._mostrarFeedback(self.rotuloStatusCaixa,
                                       f"✗ Erro ao criar caixa: {e}", "#EF4444")