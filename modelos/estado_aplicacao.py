"""
Módulo de Estado da Aplicação.
Responsável por encapsular e gerenciar todas as variáveis de estado do sistema,
como contadores de tempo, flags de execução e dados em cache.
"""

import time
from configuracao import TEMPO_CONTADOR_SEG

class EstadoAplicacao:
    """
    Classe que mantém o estado reativo da aplicação.
    
    Responsabilidade:
        Centralizar o armazenamento e manipulação de variáveis de estado,
        evitando o uso de variáveis globais dispersas.
    """

    def __init__(self):
        """Inicializa todos os atributos de estado com seus valores padrão."""
        agora = time.time()
        self.ultimo_movimento_usuario = agora
        self.ultimo_movimento_mouse = agora
        self.movendo_pelo_script = False
        self.tela_hacker_ativa = False
        
        self.texto_atual_idx = 0
        self.progresso_atual = 0
        self.tempo_restante_contador = TEMPO_CONTADOR_SEG
        self.estado_piscar = False
        
        self.dados_geolocalizacao = None
        self.contador_ataques_total = 142
        self.ultimo_feed_str = "[ESTABELECENDO MONITORAMENTO DE VETORES...]"

    def registrar_atividade_usuario(self):
        """Atualiza a marca temporal do último movimento ou tecla do usuário."""
        self.ultimo_movimento_usuario = time.time()

    def registrar_movimento_preventivo(self):
        """Atualiza a marca temporal do último movimento preventivo gerado pelo script."""
        self.ultimo_movimento_mouse = time.time()

    def resetar_sessao_hacker(self):
        """Reseta os índices de animação e timers para uma nova execução da tela hacker."""
        self.texto_atual_idx = 0
        self.progresso_atual = 0
        self.tempo_restante_contador = TEMPO_CONTADOR_SEG
        self.estado_piscar = False
        self.tela_hacker_ativa = False
        self.registrar_atividade_usuario()
        self.registrar_movimento_preventivo()

    def tempo_sem_atividade(self) -> float:
        """
        Retorna o tempo decorrido em segundos desde a última interação do usuário.
        
        Returns:
            float: Segundos de inatividade.
        """
        return time.time() - self.ultimo_movimento_usuario

    def tempo_desde_ultimo_movimento_mouse(self) -> float:
        """
        Retorna o tempo decorrido em segundos desde a última movimentação do mouse.
        
        Returns:
            float: Segundos desde o último deslocamento.
        """
        return time.time() - self.ultimo_movimento_mouse
