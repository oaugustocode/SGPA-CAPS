import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel


class TelaAcessbi(ctk.CTkToplevel):
    # Controla globalmente o fator de ampliação das fontes dos widgets na aplicação
    escalaFonteAtual = 1.0
    opcoesEscalaFonte = {
        "80%": 0.8,
        "90%": 0.9,
        "100%": 1.0,
        "110%": 1.1,
        "120%": 1.2,
        "130%": 1.3,
        "140%": 1.4,
    }

    def __init__(self, master=None):
        super().__init__(master=master)

        self.title("Configurações de Acessibilidade")
        self.geometry("900x600")
        self.attributes("-topmost", True)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])

        self.rotuloTitulo = ctk.CTkLabel(
            master=self,
            text="Configurações de Acessibilidade",
            font=("Arial", 16, "bold"),
        )
        self.rotuloTitulo.pack(pady=20)

        self.frameCentral = ctk.CTkFrame(master=self, fg_color="transparent")
        self.frameCentral.place(relx=0.5, rely=0.5, anchor="center")

        # Lê o modo visual ativo (Claro / Escuro) do CustomTkinter para iniciar o checkbox sincronizado
        self.varModoClaro = ctk.IntVar(value=1 if ctk.get_appearance_mode() == "Light" else 0)

        self.checkModoClaro = ctk.CTkCheckBox(
            master=self.frameCentral,
            text="Ativar Modo Claro",
            variable=self.varModoClaro,
            onvalue=1,
            offvalue=0,
            command=self.alternarTema,
        )
        self.checkModoClaro.pack(pady=(0, 25), padx=20)

        self.rotuloFonte = ctk.CTkLabel(
            master=self.frameCentral,
            text="Tamanho da fonte",
            font=("Arial", 14, "bold"),
        )
        self.rotuloFonte.pack(pady=(0, 10))

        # Menu para selecionar a escala dos elementos da interface (de 80% a 140%)
        self.opcoesFonte = ctk.CTkOptionMenu(
            master=self.frameCentral,
            values=list(TelaAcessbi.opcoesEscalaFonte),
            width=260,
            command=self.alterarFonte,
        )
        porcentagemAtual = f"{int(round(TelaAcessbi.escalaFonteAtual * 100))}%"
        self.opcoesFonte.set(porcentagemAtual)
        self.opcoesFonte.pack(pady=(0, 8))

        self.descricaoFonte = ctk.CTkLabel(
            master=self.frameCentral,
            text="Selecione o tamanho mais confortável para leitura.",
            wraplength=260,
            justify="center",
        )
        self.descricaoFonte.pack()

        self.rotuloCores = ctk.CTkLabel(
            master=self.frameCentral,
            text="Cores para daltonismo",
            font=("Arial", 14, "bold"),
        )
        self.rotuloCores.pack(pady=(25, 10))

        self.opcoesDaltonismo = ctk.CTkOptionMenu(
            master=self.frameCentral,
            values=list(TemaAcessivel.paletas),
            width=260,
            command=self.alterarPaleta,
        )
        self.opcoesDaltonismo.set(TemaAcessivel.perfilAtual)
        self.opcoesDaltonismo.pack(pady=(0, 8))

        self.descricaoPaleta = ctk.CTkLabel(
            master=self.frameCentral,
            text="Selecione a paleta mais confortável para sua visão.",
            wraplength=260,
            justify="center",
        )
        self.descricaoPaleta.pack()

    def alternarTema(self):
        # Alterna dinamicamente entre tema claro e escuro no motor do CustomTkinter
        if self.varModoClaro.get() == 1:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def alterarFonte(self, opcao):
        # Converte a opção percentual e aplica o fator de escala global aos componentes
        escala = TelaAcessbi.opcoesEscalaFonte[opcao]
        TelaAcessbi.escalaFonteAtual = escala
        ctk.set_widget_scaling(escala)
        if hasattr(self.master, "ajustarNavegacao"):
            self.master.ajustarNavegacao(escala)

    def alterarPaleta(self, perfil):
        # Seleciona o perfil de cor e propaga a alteração para a janela principal
        TemaAcessivel.selecionar(perfil)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.master.aplicarPaleta()
