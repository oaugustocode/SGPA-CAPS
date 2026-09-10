"""Janela popup de histórico de auditoria (prontuários reabertos ou arquivados)."""

import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel
from database.Banco import buscarLogs


class TelaHistorico(ctk.CTkToplevel):
    """Popup somente-leitura que exibe o log de ações por tipo (REABERTO ou ARQUIVADO)."""

    _TITULOS = {
        "REABERTO": "Histórico de Prontuários Reabertos",
        "ARQUIVADO": "Histórico de Prontuários Arquivados",
    }
    _SUBTITULOS = {
        "REABERTO": "Registro de todos os prontuários retirados do arquivo.",
        "ARQUIVADO": "Registro de todos os prontuários arquivados no sistema.",
    }

    def __init__(self, master=None, tipo="REABERTO"):
        super().__init__(master=master)
        self.tipo = tipo
        paleta = TemaAcessivel.obter()

        self.title(self._TITULOS.get(tipo, "Histórico"))
        self.geometry("860x560")
        self.minsize(700, 400)
        self.attributes("-topmost", True)
        self.configure(fg_color=paleta["fundo"])

        self._criarLayout(paleta)
        self._carregarRegistros()

        TemaAcessivel.registrarObservador(self._aplicarPaleta)
        self.protocol("WM_DELETE_WINDOW", self._aoFechar)

    # ─── Construção do layout ──────────────────────────────────────────────────

    def _criarLayout(self, paleta):
        ctk.CTkLabel(
            self,
            text=self._TITULOS.get(self.tipo, "Histórico"),
            font=("Arial", 20, "bold"),
            text_color=paleta["destaque"],
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            self,
            text=self._SUBTITULOS.get(self.tipo, ""),
            text_color=paleta["placeholder"],
        ).pack(pady=(0, 14))

        # Cabeçalho das colunas
        cabecalho = ctk.CTkFrame(self, fg_color=paleta["barra"], corner_radius=8)
        cabecalho.pack(fill="x", padx=24, pady=(0, 4))
        cabecalho.grid_columnconfigure(0, weight=3)
        cabecalho.grid_columnconfigure(1, weight=2)
        cabecalho.grid_columnconfigure(2, weight=2)
        cabecalho.grid_columnconfigure(3, weight=3)

        for coluna, texto in enumerate(
            ["Nome do Paciente", "Data de Nascimento", "Caixa", "Data e Hora"]
        ):
            ctk.CTkLabel(
                cabecalho,
                text=texto,
                font=("Arial", 12, "bold"),
                text_color=paleta["texto_barra"],
                anchor="w",
            ).grid(row=0, column=coluna, sticky="ew", padx=10, pady=8)

        # Área de rolagem para os registros
        self.areaRegistros = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.areaRegistros.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.areaRegistros.grid_columnconfigure(0, weight=3)
        self.areaRegistros.grid_columnconfigure(1, weight=2)
        self.areaRegistros.grid_columnconfigure(2, weight=2)
        self.areaRegistros.grid_columnconfigure(3, weight=3)

    # ─── Carregamento dos dados ────────────────────────────────────────────────

    def _carregarRegistros(self):
        for widget in self.areaRegistros.winfo_children():
            widget.destroy()

        paleta = TemaAcessivel.obter()
        registros = buscarLogs(self.tipo)

        if not registros:
            ctk.CTkLabel(
                self.areaRegistros,
                text="Nenhum registro encontrado.",
                text_color=paleta["placeholder"],
                font=("Arial", 13),
            ).pack(pady=30)
            return

        for linha_idx, registro in enumerate(registros):
            cor_fundo = paleta["card_item"] if linha_idx % 2 == 0 else paleta["card"]
            linha = ctk.CTkFrame(
                self.areaRegistros,
                fg_color=cor_fundo,
                corner_radius=7,
                border_color=paleta["borda"],
                border_width=1,
            )
            linha.grid(row=linha_idx, column=0, columnspan=4, sticky="ew", pady=3)
            linha.grid_columnconfigure(0, weight=3)
            linha.grid_columnconfigure(1, weight=2)
            linha.grid_columnconfigure(2, weight=2)
            linha.grid_columnconfigure(3, weight=3)

            caixa_texto = ""
            if registro["caixaSexo"] and registro["caixaCodigo"]:
                caixa_texto = f"{registro['caixaSexo']} • {registro['caixaCodigo']}"
            elif registro["caixaCodigo"]:
                caixa_texto = registro["caixaCodigo"]
            else:
                caixa_texto = "—"

            valores = [
                registro["nomePaciente"] or "—",
                registro["dataNascimento"] or "—",
                caixa_texto,
                registro["dataHora"] or "—",
            ]

            for col, valor in enumerate(valores):
                ctk.CTkLabel(
                    linha,
                    text=valor,
                    text_color=paleta["texto"],
                    anchor="w",
                    wraplength=180,
                    font=("Arial", 12),
                ).grid(row=0, column=col, sticky="ew", padx=10, pady=6)

    # ─── Tema reativo ──────────────────────────────────────────────────────────

    def _aplicarPaleta(self):
        paleta = TemaAcessivel.obter()
        self.configure(fg_color=paleta["fundo"])
        self._carregarRegistros()

    def _aoFechar(self):
        TemaAcessivel.removerObservador(self._aplicarPaleta)
        self.destroy()
