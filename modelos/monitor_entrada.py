"""
Módulo de Monitoramento de Dispositivos de Entrada.
Responsável por interceptar eventos globais de hardware de teclado e mouse
utilizando a biblioteca Pynput, notificando os callbacks correspondentes.
"""

from typing import Callable, Optional
from pynput import keyboard, mouse

class MonitorEntrada:
    """
    Monitor global para captura de eventos do usuário (teclado e mouse).
    
    Responsabilidade:
        Identificar quando o usuário mexe o mouse, clica, rola ou pressiona teclas,
        com tratamento especial para a tecla de escape (ESC).
    """

    def __init__(
        self,
        ao_interagir: Optional[Callable[[], None]] = None,
        ao_pressionar_esc: Optional[Callable[[], None]] = None
    ):
        """
        Inicializa os ouvintes com os callbacks definidos.
        
        Args:
            ao_interagir (Callable | None): Função chamada quando o usuário se move ou digita.
            ao_pressionar_esc (Callable | None): Função chamada quando a tecla ESC for pressionada.
        """
        self.ao_interagir = ao_interagir
        self.ao_pressionar_esc = ao_pressionar_esc
        
        self._listener_mouse = None
        self._listener_teclado = None
        self.ignorar_eventos_script = False

    def _tratar_mouse(self, *args):
        """Trata movimentação, cliques e rolagem do mouse."""
        if self.ignorar_eventos_script:
            return
        if self.ao_interagir:
            self.ao_interagir()

    def _tratar_tecla(self, tecla):
        """Trata eventos de teclas do teclado, verificando se foi a tecla ESC."""
        if tecla == keyboard.Key.esc:
            if self.ao_pressionar_esc:
                self.ao_pressionar_esc()
        else:
            if self.ao_interagir:
                self.ao_interagir()

    def iniciar(self):
        """Inicia as threads em segundo plano para escuta dos dispositivos de entrada."""
        self._listener_mouse = mouse.Listener(
            on_move=self._tratar_mouse,
            on_click=self._tratar_mouse,
            on_scroll=self._tratar_mouse
        )
        self._listener_teclado = keyboard.Listener(
            on_press=self._tratar_tecla
        )
        self._listener_mouse.start()
        self._listener_teclado.start()

    def parar(self):
        """Para e encerra a escuta dos dispositivos de entrada de forma segura."""
        if self._listener_mouse is not None:
            try:
                self._listener_mouse.stop()
            except Exception:
                pass
            self._listener_mouse = None

        if self._listener_teclado is not None:
            try:
                self._listener_teclado.stop()
            except Exception:
                pass
            self._listener_teclado = None
