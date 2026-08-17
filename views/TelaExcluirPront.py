import tkinter.messagebox as caixaMensagem

import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel
from database.Banco import excluirProntuario, listarCaixas, listarProntuariosPorCaixa


class TelaExcluirPront(ctk.CTkToplevel):
    """Janela para remover com segurança um prontuário da caixa selecionada."""

    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Excluir Prontuário")
        self.geometry("680x440")
        self.minsize(600, 400)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.attributes("-topmost", True)
        self.caixasDisponiveis = []
        self.prontuariosDisponiveis = []
        self.criarLayout()
        self.carregarCaixas()

    def criarLayout(self):
        paleta = TemaAcessivel.obter()
        ctk.CTkLabel(self, text="Excluir Prontuário", font=("Arial", 20, "bold"), text_color=paleta["destaque"]).pack(pady=(28, 5))
        ctk.CTkLabel(self, text="Selecione a caixa e depois o prontuário que deseja remover.", text_color=paleta["placeholder"]).pack(pady=(0, 18))
        quadroFormulario = ctk.CTkFrame(self, fg_color=paleta["barra"], border_color=paleta["borda"], border_width=1, corner_radius=10)
        quadroFormulario.pack(fill="x", padx=32, pady=8)
        self.criarRotulo(quadroFormulario, "Caixa *")
        self.opcaoCaixa = ctk.CTkOptionMenu(quadroFormulario, values=["Carregando..."], height=38, fg_color=paleta["hover"], button_color=paleta["destaque"], button_hover_color=paleta["hover"], command=self.aoSelecionarCaixa)
        self.opcaoCaixa.pack(fill="x", padx=18, pady=(0, 14))
        self.criarRotulo(quadroFormulario, "Prontuário *")
        self.opcaoProntuario = ctk.CTkOptionMenu(quadroFormulario, values=["Selecione uma caixa primeiro"], height=38, fg_color=paleta["hover"], button_color=paleta["destaque"], button_hover_color=paleta["hover"])
        self.opcaoProntuario.pack(fill="x", padx=18, pady=(0, 18))
        self.botaoExcluir = ctk.CTkButton(quadroFormulario, text="Excluir prontuário selecionado", height=40, fg_color="#C62828", hover_color="#8E1B1B", font=("Arial", 14, "bold"), command=self.confirmarExclusao)
        self.botaoExcluir.pack(pady=(0, 8))
        self.rotuloStatus = ctk.CTkLabel(quadroFormulario, text="", height=28)
        self.rotuloStatus.pack(pady=(0, 12))
        ctk.CTkLabel(self, text="A exclusão é permanente. Confira a seleção antes de confirmar.", text_color="#EF4444", font=("Arial", 12)).pack(pady=(12, 0))

    def criarRotulo(self, quadro, texto):
        ctk.CTkLabel(quadro, text=texto, anchor="w", font=("Arial", 13), text_color=TemaAcessivel.obter()["texto"]).pack(fill="x", padx=18, pady=(14, 3))

    def carregarCaixas(self):
        self.caixasDisponiveis = listarCaixas()
        if not self.caixasDisponiveis:
            self.opcaoCaixa.configure(values=["Nenhuma caixa encontrada"])
            self.opcaoCaixa.set("Nenhuma caixa encontrada")
            self.botaoExcluir.configure(state="disabled")
            return
        opcoesCaixa = [f"{caixa['codigo']} — {caixa['sexo']}" for caixa in self.caixasDisponiveis]
        self.opcaoCaixa.configure(values=opcoesCaixa)
        self.opcaoCaixa.set(opcoesCaixa[0])
        self.aoSelecionarCaixa(opcoesCaixa[0])

    def aoSelecionarCaixa(self, caixaSelecionada):
        caixaId = next((caixa["id"] for caixa in self.caixasDisponiveis if f"{caixa['codigo']} — {caixa['sexo']}" == caixaSelecionada), None)
        self.prontuariosDisponiveis = listarProntuariosPorCaixa(caixaId) if caixaId else []
        if not self.prontuariosDisponiveis:
            self.opcaoProntuario.configure(values=["Nenhum prontuário nesta caixa"])
            self.opcaoProntuario.set("Nenhum prontuário nesta caixa")
            self.botaoExcluir.configure(state="disabled")
            return
        opcoesProntuario = [f"{prontuario['nomePaciente']} | CNS {prontuario['cns']}" for prontuario in self.prontuariosDisponiveis]
        self.opcaoProntuario.configure(values=opcoesProntuario)
        self.opcaoProntuario.set(opcoesProntuario[0])
        self.botaoExcluir.configure(state="normal")

    def confirmarExclusao(self):
        prontuarioSelecionado = self.opcaoProntuario.get()
        prontuarioId = next((prontuario["id"] for prontuario in self.prontuariosDisponiveis if f"{prontuario['nomePaciente']} | CNS {prontuario['cns']}" == prontuarioSelecionado), None)
        if prontuarioId is None:
            self.mostrarStatus("Selecione um prontuário válido.", "#EF4444")
            return
        confirmou = caixaMensagem.askyesno("Confirmar exclusão", f"Deseja excluir permanentemente o prontuário:\n\n{prontuarioSelecionado}?", parent=self)
        if not confirmou:
            return
        if excluirProntuario(prontuarioId):
            self.mostrarStatus("Prontuário excluído com sucesso.", "#4ADE80")
            self.aoSelecionarCaixa(self.opcaoCaixa.get())
        else:
            self.mostrarStatus("Não foi possível excluir o prontuário.", "#EF4444")

    def mostrarStatus(self, texto, cor):
        self.rotuloStatus.configure(text=texto, text_color=cor)
        self.after(4000, lambda: self.rotuloStatus.configure(text=""))
