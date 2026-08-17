import customtkinter as ctk
from components.TemaAcessivel import TemaAcessivel


class TelaAjuda(ctk.CTkToplevel):
    """Janela modal com orientações objetivas sobre os fluxos do sistema."""

    def __init__(self, *args, corFundo=None, **kwargs):
        super().__init__(*args, fg_color=corFundo, **kwargs)
        self.title("Central de Ajuda")
        self.geometry("850x600")
        self.minsize(680, 500)
        self.attributes("-topmost", True)
        self.configure(fg_color=TemaAcessivel.obter()["fundo"])
        self.criarConteudo()

    def criarConteudo(self):
        paleta = TemaAcessivel.obter()
        ctk.CTkLabel(self, text="Guia de Como Utilizar o Sistema", font=("Arial", 20, "bold"), text_color=paleta["destaque"]).pack(pady=(24, 5))
        ctk.CTkLabel(self, text="Encontre, cadastre e organize prontuários de forma rápida.", text_color=paleta["placeholder"]).pack(pady=(0, 15))
        areaInstrucoes = ctk.CTkScrollableFrame(self, fg_color="transparent")
        areaInstrucoes.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        instrucoes = [
            ("1. Buscar um prontuário", "Na tela inicial, digite ao menos duas letras do nome ou parte do CNS. Escolha um resultado ou pressione Enter para abrir o primeiro."),
            ("2. Consultar caixas", "Use Caixa Masculina ou Caixa Feminina para navegar pelas caixas. Os botões de A a Z filtram os códigos e Carregar mais exibe os próximos resultados."),
            ("3. Adicionar prontuário", "Abra Adicionar Prontuário, preencha nome, CNS de 15 dígitos, sexo e caixa. Caso necessário, crie uma nova caixa na parte inferior da mesma tela."),
            ("4. Excluir prontuário", "Abra Excluir Prontuário na barra superior. Selecione a caixa, escolha o prontuário e confirme a exclusão. Essa ação é permanente."),
            ("5. Acessibilidade", "Use o ícone de acessibilidade no topo para ajustar a visualização conforme sua necessidade."),
        ]
        for titulo, descricao in instrucoes:
            self.criarCartaoInstrucao(areaInstrucoes, titulo, descricao)

    def criarCartaoInstrucao(self, areaInstrucoes, titulo, descricao):
        paleta = TemaAcessivel.obter()
        cartao = ctk.CTkFrame(areaInstrucoes, fg_color=paleta["barra"], border_color=paleta["borda"], border_width=1, corner_radius=10)
        cartao.pack(fill="x", pady=6)
        ctk.CTkLabel(cartao, text=titulo, font=("Arial", 15, "bold"), anchor="w", text_color=paleta["texto"]).pack(fill="x", padx=14, pady=(11, 3))
        ctk.CTkLabel(cartao, text=descricao, justify="left", anchor="w", wraplength=740, text_color=paleta["placeholder"]).pack(fill="x", padx=14, pady=(0, 11))
