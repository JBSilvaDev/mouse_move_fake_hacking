"""
Módulo de Serviço de Controle do Mouse.
Responsável pela movimentação automatizada preventiva do cursor do mouse,
mantendo o status do usuário ativo em ferramentas corporativas (ex: Microsoft Teams, Slack).
"""

import random
import ctypes
import pyautogui

# Desativa o recurso failsafe do PyAutoGUI para evitar exceções caso o cursor toque os cantos da tela
pyautogui.FAILSAFE = False

# Constantes da API do Windows para controle de energia e entrada
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

VK_F15 = 0x7E  # Tecla virtual F15 (inofensiva, sem caractere ou atalho associado)
KEYEVENTF_KEYUP = 0x0002

class ServicoMouse:
    """
    Serviço que encapsula a automação de movimentação do mouse e prevenção de inatividade.
    
    Responsabilidade:
        Efetuar pequenos deslocamentos randômicos no cursor e simular pulsos
        nativos de atividade para manter o Windows acordado e ferramentas corporativas
        (ex: Microsoft Teams, Slack) com status ativo/online ininterrupto.
    """

    def __init__(self, variacao_maxima: int = 15, duracao: float = 0.3):
        """
        Inicializa o serviço de mouse com os parâmetros de deslocamento.
        
        Args:
            variacao_maxima (int): Pixels máximos de deslocamento em X e Y.
            duracao (float): Tempo em segundos para a animação do movimento suave.
        """
        self.variacao_maxima = variacao_maxima
        self.duracao = duracao

    def manter_sistema_acordado(self):
        """
        Informa ao kernel do Windows que o sistema e o display devem permanecer acordados,
        evitando suspensão, tela preta ou bloqueio de tela por inatividade corporativa.
        """
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
        except Exception:
            pass

    def liberar_sistema(self):
        """Restaura o comportamento normal de economia de energia do Windows."""
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        except Exception:
            pass

    def simular_pulso_atividade(self):
        """
        Emite um pressionamento e soltura ultrarrápido da tecla virtual F15 (0x7E).
        Essa tecla é completamente neutra e inofensiva no Windows, mas gera um evento
        real no subsistema de entrada, zerando o contador GetLastInputInfo consultado
        pelo Microsoft Teams e Slack.
        """
        try:
            ctypes.windll.user32.keybd_event(VK_F15, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_F15, 0, KEYEVENTF_KEYUP, 0)
        except Exception:
            pass

    def mover_preventivamente(self) -> tuple[int, int]:
        """
        Executa a rotina completa preventiva contra inatividade:
        1. Mantém a tela e o sistema despertos (SetThreadExecutionState).
        2. Envia um pulso neutro de atividade para zerar o idle timer do Teams (VK_F15).
        3. Move suavemente o cursor em coordenadas relativas seguras.
        
        Returns:
            tuple[int, int]: Nova coordenada (x, y) do cursor após o movimento.
        """
        self.manter_sistema_acordado()
        self.simular_pulso_atividade()

        x_atual, y_atual = pyautogui.position()
        delta_x = random.randint(-self.variacao_maxima, self.variacao_maxima)
        delta_y = random.randint(-self.variacao_maxima, self.variacao_maxima)
        novo_x = max(10, x_atual + delta_x)
        novo_y = max(10, y_atual + delta_y)

        pyautogui.moveTo(novo_x, novo_y, duration=self.duracao)
        return novo_x, novo_y

