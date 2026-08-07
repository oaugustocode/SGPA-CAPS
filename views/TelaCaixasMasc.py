from views.TelaCaixas import TelaCaixas


class TelaCaixasMasc(TelaCaixas):
    """Especialização da tela de caixas pré-configurada para o sexo Masculino."""

    def __init__(self, master, **kwargs):
        super().__init__(master=master, sexo="Masculino", titulo="Caixas Masculinas")

