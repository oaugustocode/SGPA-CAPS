"""Arquivo para inicializar a aplicação SGPA-CAPS."""

from views.TelaPrincipal import TelaPrincipal

if __name__ == "__main__":
    # Inicializa e executa o loop principal da interface gráfica
    aplicacao = TelaPrincipal()
    aplicacao.mainloop()