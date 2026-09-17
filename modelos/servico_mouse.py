"""
Módulo de Serviço de Controle do Mouse.
Responsável pela movimentação automatizada preventiva do cursor do mouse,
mantendo o status do usuário ativo em ferramentas corporativas (ex: Microsoft Teams, Slack).
"""

import random
import pyautogui

# Desativa o recurso failsafe do PyAutoGUI para evitar exceções caso o cursor toque os cantos da tela
pyautogui.FAILSAFE = False

class ServicoMouse:
    """
    Serviço que encapsula a automação de movimentação do mouse.
    
    Responsabilidade:
        Efetuar pequenos deslocamentos randômicos no cursor sem causar interferência
        perceptível e sem ser interpretado como movimento intencional do usuário.
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

    def mover_preventivamente(self) -> tuple[int, int]:
        """
        Calcula uma nova posição próxima da atual e move suavemente o cursor.
        
        Returns:
            tuple[int, int]: Nova coordenada (x, y) do cursor após o movimento.
        """
        x_atual, y_atual = pyautogui.position()
        delta_x = random.randint(-self.variacao_maxima, self.variacao_maxima)
        delta_y = random.randint(-self.variacao_maxima, self.variacao_maxima)
        novo_x = x_atual + delta_x
        novo_y = y_atual + delta_y

        pyautogui.moveTo(novo_x, novo_y, duration=self.duracao)
        return novo_x, novo_y
