"""
Ponto de Entrada Principal da Aplicação (main.pyw).
Inicializa o loop de eventos raiz do Tkinter e instancia o Apresentador Principal
no padrão arquitetural MVP (Model-View-Presenter).
Executável em segundo plano sem janela de console através do executável pythonw.exe.
"""

import tkinter as tk
from apresentadores.apresentador_principal import ApresentadorPrincipal

def main():
    """
    Função principal de inicialização do programa.
    Cria a raiz do Tkinter, oculta a janela padrão e dispara o ciclo de vida do MVP.
    """
    print("==========================================================")
    print("    ANTI-AUSENTE HACKER - ARQUITETURA MVP (MAIN.PYW)     ")
    print("==========================================================")

    # Criação da janela raiz oculta do Tkinter (necessária para gerenciar janelas e timers)
    root = tk.Tk()
    root.withdraw()

    # Criação e inicialização do Apresentador Principal
    apresentador = ApresentadorPrincipal(root)
    apresentador.inicializar()

    # Execução do loop principal de mensagens
    try:
        root.mainloop()
    except KeyboardInterrupt:
        apresentador.encerrar_aplicacao()

if __name__ == "__main__":
    main()
