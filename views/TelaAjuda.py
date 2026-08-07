import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel


class TelaAjuda(ctk.CTkToplevel):
    """Janela modal para exibição do guia e instruções de uso do sistema."""

    def __init__(self, *args, corFundo=None, **kwargs):
        super().__init__(*args, fg_color=corFundo, **kwargs)

        self.title("Central de Ajuda")
        self.geometry("1200x600")

        # Mantém a janela de ajuda sempre em primeiro plano em relação à janela principal
        self.attributes("-topmost", True)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])

        self.rotuloTitulo = ctk.CTkLabel(
            master=self,
            text="Guia de Como Utilizar o Sistema",
            font=("Arial", 16, "bold"),
        )
        self.rotuloTitulo.pack(pady=20)

