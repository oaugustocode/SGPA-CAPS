from views.TelaCaixas import TelaCaixas


class TelaCaixasFem(TelaCaixas):
    """Especialização da tela de caixas pré-configurada para o sexo Feminino."""

    def __init__(self, master, **kwargs):
        super().__init__(master=master, sexo="Feminino", titulo="Caixas Femininas", **kwargs)

