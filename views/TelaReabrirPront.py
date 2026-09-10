"""Tela para reabertura de prontuários arquivados com registro de auditoria."""

import datetime
import tkinter.messagebox as caixaMensagem

import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel
from database.Banco import (
    excluirProntuario,
    listarCaixas,
    listarProntuariosPorCaixa,
    buscarProntuario,
    registrarLog,
)
from views.TelaHistorico import TelaHistorico


class TelaReabrirPront(ctk.CTkToplevel):
    """Janela para reabrir (retirar do arquivo) um prontuário com log de auditoria."""

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.title("Reabrir Prontuário")
        self.geometry("680x560")
        self.minsize(600, 480)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.attributes("-topmost", True)
        self.caixasDisponiveis = []
        self.prontuariosDisponiveis = []
        self._janelaHistorico = None

        self.areaConteudo = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
        )
        self.areaConteudo.pack(fill="both", expand=True)
        self.criarLayout()
        self.carregarCaixas()

    # ─── Layout ────────────────────────────────────────────────────────────────

    def criarLayout(self):
        paleta = TemaAcessivel.obter()

        ctk.CTkLabel(
            self.areaConteudo, text="Reabrir Prontuário",
            font=("Arial", 20, "bold"), text_color=paleta["destaque"],
        ).pack(pady=(28, 5))

        ctk.CTkLabel(
            self.areaConteudo,
            text="Selecione a caixa e o prontuário que deseja reabrir.",
            text_color=paleta["placeholder"],
        ).pack(pady=(0, 18))

        # ── Formulário de seleção ──────────────────────────────────────────────
        quadroFormulario = ctk.CTkFrame(
            self.areaConteudo, fg_color=paleta["barra"],
            border_color=paleta["borda"], border_width=1, corner_radius=10,
        )
        quadroFormulario.pack(fill="x", padx=32, pady=8)

        self._criarRotulo(quadroFormulario, "Caixa *")
        self.opcaoCaixa = ctk.CTkOptionMenu(
            quadroFormulario, values=["Carregando..."], height=38,
            fg_color=paleta["hover"], button_color=paleta["destaque"],
            button_hover_color=paleta["hover"],
            command=self.aoSelecionarCaixa,
        )
        self.opcaoCaixa.pack(fill="x", padx=18, pady=(0, 14))

        self._criarRotulo(quadroFormulario, "Prontuário *")
        self.opcaoProntuario = ctk.CTkOptionMenu(
            quadroFormulario, values=["Selecione uma caixa primeiro"], height=38,
            fg_color=paleta["hover"], button_color=paleta["destaque"],
            button_hover_color=paleta["hover"],
        )
        self.opcaoProntuario.pack(fill="x", padx=18, pady=(0, 18))

        self.botaoReabrir = ctk.CTkButton(
            quadroFormulario,
            text="Reabrir prontuário selecionado",
            height=40, fg_color="#1565C0", hover_color="#0D47A1",
            font=("Arial", 14, "bold"),
            command=self.confirmarReabertura,
        )
        self.botaoReabrir.pack(pady=(0, 8))

        self.rotuloStatus = ctk.CTkLabel(quadroFormulario, text="", height=28)
        self.rotuloStatus.pack(pady=(0, 12))

        ctk.CTkLabel(
            self.areaConteudo,
            text="Ao reabrir, o prontuário será removido do arquivo e o evento ficará registrado no histórico.",
            text_color="#EF4444", font=("Arial", 12), wraplength=580,
        ).pack(pady=(8, 14))

        # ── Botão de histórico ─────────────────────────────────────────────────
        ctk.CTkButton(
            self.areaConteudo,
            text="📋  Histórico de Prontuários Reabertos",
            height=38, corner_radius=8,
            fg_color=paleta["barra"], hover_color=paleta["hover"],
            text_color=paleta["texto_barra"],
            border_color=paleta["borda"], border_width=1,
            font=("Arial", 13),
            command=self.abrirHistorico,
        ).pack(padx=32, pady=(0, 20), fill="x")

    def _criarRotulo(self, quadro, texto):
        ctk.CTkLabel(
            quadro, text=texto, anchor="w",
            font=("Arial", 13),
            text_color=TemaAcessivel.obter()["texto"],
        ).pack(fill="x", padx=18, pady=(14, 3))

    # ─── Dados ─────────────────────────────────────────────────────────────────

    def carregarCaixas(self):
        self.caixasDisponiveis = listarCaixas()
        if not self.caixasDisponiveis:
            self.opcaoCaixa.configure(values=["Nenhuma caixa encontrada"])
            self.opcaoCaixa.set("Nenhuma caixa encontrada")
            self.botaoReabrir.configure(state="disabled")
            return
        opcoesCaixa = [
            f"{caixa['codigo']} — {caixa['sexo']}"
            for caixa in self.caixasDisponiveis
        ]
        self.opcaoCaixa.configure(values=opcoesCaixa)
        self.opcaoCaixa.set(opcoesCaixa[0])
        self.aoSelecionarCaixa(opcoesCaixa[0])

    def aoSelecionarCaixa(self, caixaSelecionada):
        caixaId = next(
            (c["id"] for c in self.caixasDisponiveis
             if f"{c['codigo']} — {c['sexo']}" == caixaSelecionada),
            None,
        )
        self.prontuariosDisponiveis = (
            listarProntuariosPorCaixa(caixaId) if caixaId else []
        )
        if not self.prontuariosDisponiveis:
            self.opcaoProntuario.configure(values=["Nenhum prontuário nesta caixa"])
            self.opcaoProntuario.set("Nenhum prontuário nesta caixa")
            self.botaoReabrir.configure(state="disabled")
            return
        opcoesProntuario = [
            f"{p['nomePaciente']} | CNS {p['cns']}"
            for p in self.prontuariosDisponiveis
        ]
        self.opcaoProntuario.configure(values=opcoesProntuario)
        self.opcaoProntuario.set(opcoesProntuario[0])
        self.botaoReabrir.configure(state="normal")

    # ─── Ações ─────────────────────────────────────────────────────────────────

    def confirmarReabertura(self):
        prontuarioSelecionado = self.opcaoProntuario.get()
        prontuarioId = next(
            (p["id"] for p in self.prontuariosDisponiveis
             if f"{p['nomePaciente']} | CNS {p['cns']}" == prontuarioSelecionado),
            None,
        )
        if prontuarioId is None:
            self._mostrarStatus("Selecione um prontuário válido.", "#EF4444")
            return

        confirmou = caixaMensagem.askyesno(
            "Confirmar reabertura",
            f"Deseja reabrir o prontuário:\n\n{prontuarioSelecionado}?\n\n"
            "Ele será removido do arquivo e o evento ficará no histórico.",
            parent=self,
        )
        if not confirmou:
            return

        # Captura os dados completos antes de excluir
        dadosCompletos = buscarProntuario(prontuarioId)

        if excluirProntuario(prontuarioId):
            # Registra o log de auditoria
            dataHora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            registrarLog(
                tipo="REABERTO",
                nomePaciente=dadosCompletos["nomePaciente"] if dadosCompletos else prontuarioSelecionado,
                dataNascimento=dadosCompletos["dataNascimento"] if dadosCompletos else None,
                caixaCodigo=dadosCompletos["caixaCodigo"] if dadosCompletos else None,
                caixaSexo=dadosCompletos["caixaSexo"] if dadosCompletos else None,
                dataHora=dataHora,
            )
            self._mostrarStatus("Prontuário reaberto e registrado no histórico.", "#4ADE80")
            self.aoSelecionarCaixa(self.opcaoCaixa.get())

            # Atualiza o histórico se já estiver aberto
            if self._janelaHistorico and self._janelaHistorico.winfo_exists():
                self._janelaHistorico._carregarRegistros()
        else:
            self._mostrarStatus("Não foi possível reabrir o prontuário.", "#EF4444")

    def abrirHistorico(self):
        if self._janelaHistorico and self._janelaHistorico.winfo_exists():
            self._janelaHistorico.lift()
            self._janelaHistorico.focus_force()
            return
        self._janelaHistorico = TelaHistorico(master=self, tipo="REABERTO")

    def _mostrarStatus(self, texto, cor):
        self.rotuloStatus.configure(text=texto, text_color=cor)
        self.after(4000, lambda: self.rotuloStatus.configure(text=""))
