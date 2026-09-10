"""Tela de arquivamento de prontuários com validação de código de caixa e log de auditoria."""

import datetime
import re
import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel
from database.Banco import listarCaixas, criarCaixa, criarProntuario, registrarLog
from views.TelaHistorico import TelaHistorico


# Padrão aceito: letra A-Z (maiúscula), espaço opcional, um ou mais dígitos.
# Exemplos válidos: A1, B12, A 1, Z99
_PADRAO_CODIGO_CAIXA = re.compile(r"^[A-Z]\s?\d+$")


class TelaArquivarPront(ctk.CTkToplevel):
    """Janela para arquivar (cadastrar) um novo prontuário no sistema."""

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.title("Arquivar Prontuário")
        self.geometry("900x860")
        self.minsize(720, 620)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.attributes("-topmost", True)
        self.cacheCaixas = []
        self._janelaHistorico = None

        self.areaConteudo = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
        )
        self.areaConteudo.pack(fill="both", expand=True)
        self.criarLayoutFormulario()

    # ─── Layout principal ──────────────────────────────────────────────────────

    def criarLayoutFormulario(self):
        paleta = TemaAcessivel.obter()

        ctk.CTkLabel(
            self.areaConteudo, text="Arquivar Prontuário",
            font=("Arial", 20, "bold"),
            text_color=("", "#FFFFFF"),
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self.areaConteudo,
            text="Preencha os dados abaixo para arquivar um novo prontuário.",
            text_color=paleta["placeholder"],
        ).pack(pady=(0, 16))

        # ── Seção: dados do paciente ───────────────────────────────────────────
        self.frameFormulario = ctk.CTkFrame(
            self.areaConteudo, fg_color=paleta["barra"],
            border_color=paleta["borda"], border_width=1, corner_radius=10,
        )
        self.frameFormulario.pack(fill="x", padx=30, pady=(0, 10))
        f = self.frameFormulario

        self._criarRotulo(f, "Nome do Paciente *")
        self.entradaNome = ctk.CTkEntry(
            f, placeholder_text="Nome completo do paciente",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaNome.pack(fill="x", padx=16, pady=(0, 10))

        # Linha Pai / Mãe
        linhaPaiMae = ctk.CTkFrame(f, fg_color="transparent")
        linhaPaiMae.pack(fill="x", padx=16, pady=(0, 10))
        linhaPaiMae.grid_columnconfigure(0, weight=1)
        linhaPaiMae.grid_columnconfigure(1, weight=1)

        blocoPai = ctk.CTkFrame(linhaPaiMae, fg_color="transparent")
        blocoPai.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoPai, "Nome do Pai", pack=False)
        self.entradaPai = ctk.CTkEntry(
            blocoPai, placeholder_text="Nome do pai",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaPai.pack(fill="x")

        blocoMae = ctk.CTkFrame(linhaPaiMae, fg_color="transparent")
        blocoMae.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoMae, "Nome da Mãe", pack=False)
        self.entradaMae = ctk.CTkEntry(
            blocoMae, placeholder_text="Nome da mãe",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaMae.pack(fill="x")

        # Data de Nascimento
        self._criarRotulo(f, "Data de Nascimento (DD/MM/AAAA) *")
        self.entradaDataNasc = ctk.CTkEntry(
            f, placeholder_text="DD/MM/AAAA",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaDataNasc.pack(fill="x", padx=16, pady=(0, 10))

        # CNS + Sexo
        linhaCnsSexo = ctk.CTkFrame(f, fg_color="transparent")
        linhaCnsSexo.pack(fill="x", padx=16, pady=(0, 10))
        linhaCnsSexo.grid_columnconfigure(0, weight=3)
        linhaCnsSexo.grid_columnconfigure(1, weight=1)

        blocoCns = ctk.CTkFrame(linhaCnsSexo, fg_color="transparent")
        blocoCns.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoCns, "CNS (5 dígitos) *", pack=False)
        self.entradaCns = ctk.CTkEntry(
            blocoCns, placeholder_text="00000",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaCns.pack(fill="x")

        blocoSexo = ctk.CTkFrame(linhaCnsSexo, fg_color="transparent")
        blocoSexo.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoSexo, "Sexo *", pack=False)
        self.opcaoSexo = ctk.CTkOptionMenu(
            blocoSexo, values=["M", "F"], height=36, width=100,
            fg_color=paleta["hover"], button_color=paleta["destaque"],
            button_hover_color=paleta["hover"],
        )
        self.opcaoSexo.pack(fill="x")

        # Caixa
        self._criarRotulo(f, "Caixa *")
        self.opcaoCaixa = ctk.CTkOptionMenu(
            f, values=["Carregando..."], height=36,
            fg_color=paleta["hover"], button_color=paleta["destaque"],
            button_hover_color=paleta["hover"],
        )
        self.opcaoCaixa.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            f, text="Arquivar Prontuário",
            height=40, corner_radius=8,
            fg_color=paleta["destaque"], hover_color=paleta["hover"],
            text_color="#001D3D", font=("Arial", 14, "bold"),
            command=self.salvarProntuario,
        ).pack(pady=(0, 16))

        self.rotuloStatus = ctk.CTkLabel(f, text="", height=20, text_color="#4ADE80")
        self.rotuloStatus.pack(pady=(0, 10))

        # ── Separador ──────────────────────────────────────────────────────────
        ctk.CTkFrame(self.areaConteudo, height=2, fg_color=paleta["borda"]).pack(
            fill="x", padx=30, pady=(6, 10)
        )

        # ── Seção: criar nova caixa ────────────────────────────────────────────
        self.frameCaixa = ctk.CTkFrame(
            self.areaConteudo, fg_color=paleta["barra"],
            border_color=paleta["borda"], border_width=1, corner_radius=10,
        )
        self.frameCaixa.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            self.frameCaixa, text="Criar Nova Caixa",
            font=("Arial", 16, "bold"), text_color=paleta["destaque"],
        ).pack(pady=(14, 8))

        linhaCaixa = ctk.CTkFrame(self.frameCaixa, fg_color="transparent")
        linhaCaixa.pack(fill="x", padx=16, pady=(0, 10))
        linhaCaixa.grid_columnconfigure(0, weight=2)
        linhaCaixa.grid_columnconfigure(1, weight=1)

        blocoCodigo = ctk.CTkFrame(linhaCaixa, fg_color="transparent")
        blocoCodigo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._criarRotulo(blocoCodigo, "Código da Caixa  (ex: A1, B2, A 1)", pack=False)
        self.entradaCodigo = ctk.CTkEntry(
            blocoCodigo, placeholder_text="Ex: A1, B2, A 1...",
            height=36, fg_color=paleta["hover"], border_width=0,
            text_color=paleta["texto"], placeholder_text_color=paleta["placeholder"],
        )
        self.entradaCodigo.pack(fill="x")

        blocoSexoCaixa = ctk.CTkFrame(linhaCaixa, fg_color="transparent")
        blocoSexoCaixa.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self._criarRotulo(blocoSexoCaixa, "Sexo da Caixa", pack=False)
        self.opcaoSexoCaixa = ctk.CTkOptionMenu(
            blocoSexoCaixa, values=["Masculino", "Feminino"],
            height=36, width=140,
            fg_color=paleta["hover"], button_color=paleta["destaque"],
            button_hover_color=paleta["hover"],
        )
        self.opcaoSexoCaixa.pack(fill="x")

        ctk.CTkButton(
            self.frameCaixa, text="Criar Caixa",
            height=36, corner_radius=8,
            fg_color=paleta["destaque"], hover_color=paleta["hover"],
            text_color="#001D3D", font=("Arial", 13, "bold"),
            command=self.salvarCaixa,
        ).pack(pady=(4, 10))

        self.rotuloStatusCaixa = ctk.CTkLabel(
            self.frameCaixa, text="", height=20, text_color="#4ADE80",
        )
        self.rotuloStatusCaixa.pack(pady=(0, 10))

        # ── Botão histórico ────────────────────────────────────────────────────
        ctk.CTkButton(
            self.areaConteudo,
            text="📋  Histórico de Prontuários Arquivados",
            height=38, corner_radius=8,
            fg_color=paleta["barra"], hover_color=paleta["hover"],
            text_color=paleta["texto_barra"],
            border_color=paleta["borda"], border_width=1,
            font=("Arial", 13),
            command=self.abrirHistorico,
        ).pack(padx=30, pady=(0, 24), fill="x")

        self.atualizarDropdownCaixas()

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def _criarRotulo(self, master, texto, pack=True):
        paleta = TemaAcessivel.obter()
        label = ctk.CTkLabel(
            master, text=texto, anchor="w",
            font=("Arial", 13), text_color=paleta["texto"],
        )
        if pack:
            label.pack(fill="x", padx=16, pady=(10, 2))
        else:
            label.pack(fill="x", pady=(0, 2))
        return label

    def atualizarDropdownCaixas(self):
        self.cacheCaixas = listarCaixas()
        if self.cacheCaixas:
            opcoes = [f"{c['codigo']} — {c['sexo']}" for c in self.cacheCaixas]
            self.opcaoCaixa.configure(values=opcoes)
            self.opcaoCaixa.set(opcoes[0])
        else:
            self.opcaoCaixa.configure(values=["Nenhuma caixa encontrada"])
            self.opcaoCaixa.set("Nenhuma caixa encontrada")

    def _mostrarFeedback(self, label, texto, cor):
        label.configure(text=texto, text_color=cor)
        self.after(4000, lambda: label.configure(text=""))

    # ─── Ações ─────────────────────────────────────────────────────────────────

    def salvarProntuario(self):
        nome = self.entradaNome.get().strip()
        pai = self.entradaPai.get().strip() or None
        mae = self.entradaMae.get().strip() or None
        dataNascTexto = self.entradaDataNasc.get().strip()
        cns = self.entradaCns.get().strip()
        sexo = self.opcaoSexo.get()

        if not nome:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Nome do paciente é obrigatório.", "#EF4444")
            return

        if not dataNascTexto:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Data de nascimento é obrigatória.", "#EF4444")
            return

        try:
            dataNasc = datetime.datetime.strptime(dataNascTexto, "%d/%m/%Y").date()
        except ValueError:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Data inválida. Use DD/MM/AAAA.", "#EF4444")
            return

        hoje = datetime.date.today()
        if dataNasc > hoje:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Data não pode ser no futuro.", "#EF4444")
            return

        idadeAnos = hoje.year - dataNasc.year - (
            (hoje.month, hoje.day) < (dataNasc.month, dataNasc.day)
        )
        if idadeAnos >= 18:
            self._mostrarFeedback(
                self.rotuloStatus,
                "⚠ Permitido apenas crianças e adolescentes até 17 anos e 11 meses.",
                "#EF4444",
            )
            return

        if not cns or len(cns) != 5 or not cns.isdigit():
            self._mostrarFeedback(self.rotuloStatus, "⚠ CNS deve ter exatamente 5 dígitos numéricos.", "#EF4444")
            return

        if not self.cacheCaixas:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Nenhuma caixa disponível. Crie uma caixa primeiro.", "#EF4444")
            return

        selecionado = self.opcaoCaixa.get()
        caixaId = None
        caixaSelecionada = None
        for caixa in self.cacheCaixas:
            if f"{caixa['codigo']} — {caixa['sexo']}" == selecionado:
                caixaId = caixa["id"]
                caixaSelecionada = caixa
                break

        if caixaId is None:
            self._mostrarFeedback(self.rotuloStatus, "⚠ Selecione uma caixa válida.", "#EF4444")
            return

        try:
            criarProntuario(nome, pai, mae, dataNascTexto, sexo, cns, caixaId)

            # Registra o log de arquivamento
            dataHora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            registrarLog(
                tipo="ARQUIVADO",
                nomePaciente=nome,
                dataNascimento=dataNascTexto,
                caixaCodigo=caixaSelecionada["codigo"] if caixaSelecionada else None,
                caixaSexo=caixaSelecionada["sexo"] if caixaSelecionada else None,
                dataHora=dataHora,
            )

            self._mostrarFeedback(self.rotuloStatus, "✓ Prontuário arquivado com sucesso!", "#4ADE80")
            self.entradaNome.delete(0, "end")
            self.entradaPai.delete(0, "end")
            self.entradaMae.delete(0, "end")
            self.entradaDataNasc.delete(0, "end")
            self.entradaCns.delete(0, "end")

            # Atualiza histórico se aberto
            if self._janelaHistorico and self._janelaHistorico.winfo_exists():
                self._janelaHistorico._carregarRegistros()
        except Exception as e:
            self._mostrarFeedback(self.rotuloStatus, f"✗ Erro ao arquivar: {e}", "#EF4444")

    def salvarCaixa(self):
        """Valida e cria uma nova caixa. Código: letra A-Z seguida de dígitos (ex: A1, B2, A 1)."""
        # Normaliza: converte para maiúscula e remove espaço interno (A 1 → A1)
        codigo_raw = self.entradaCodigo.get().strip().upper()
        codigo = codigo_raw.replace(" ", "")  # normaliza A 1 → A1 para armazenamento

        if not codigo_raw:
            self._mostrarFeedback(self.rotuloStatusCaixa, "⚠ Código da caixa é obrigatório.", "#EF4444")
            return

        # Valida o formato: letra + (espaço opcional) + dígitos
        if not _PADRAO_CODIGO_CAIXA.match(codigo_raw):
            self._mostrarFeedback(
                self.rotuloStatusCaixa,
                "⚠ Código inválido. Use uma letra (A-Z) seguida de número(s). Ex: A1, B2, A 1.",
                "#EF4444",
            )
            return

        sexo = self.opcaoSexoCaixa.get()

        try:
            criarCaixa(codigo, sexo)
            self._mostrarFeedback(
                self.rotuloStatusCaixa, f"✓ Caixa {codigo} ({sexo}) criada!", "#4ADE80"
            )
            self.entradaCodigo.delete(0, "end")
            self.atualizarDropdownCaixas()
        except Exception as e:
            msg = str(e)
            if "UNIQUE" in msg:
                self._mostrarFeedback(
                    self.rotuloStatusCaixa,
                    "⚠ Já existe uma caixa com este código e sexo.",
                    "#EF4444",
                )
            else:
                self._mostrarFeedback(self.rotuloStatusCaixa, f"✗ Erro ao criar caixa: {e}", "#EF4444")

    def abrirHistorico(self):
        if self._janelaHistorico and self._janelaHistorico.winfo_exists():
            self._janelaHistorico.lift()
            self._janelaHistorico.focus_force()
            return
        self._janelaHistorico = TelaHistorico(master=self, tipo="ARQUIVADO")
