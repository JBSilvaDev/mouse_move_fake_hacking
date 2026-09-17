"""
Módulo de Visão da Bandeja do Sistema (System Tray).
Responsável por criar o ícone na área de notificação do Windows utilizando Pystray,
oferecendo opções de menu para verificação de status e encerramento seguro do programa.
"""

import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray

class VisaoBandeja:
    """
    Gerenciador visual do ícone na bandeja do sistema.
    
    Responsabilidade:
        Desenhar o ícone tático minimalista da aplicação, manter o menu de contexto
        e despachar o comando de saída quando solicitado pelo usuário.
    """

    def __init__(self, ao_sair: Optional[Callable[[], None]] = None):
        """
        Inicializa a visão da bandeja com o callback de finalização.
        
        Args:
            ao_sair (Callable | None): Callback a ser disparado ao clicar em 'Sair / Fechar'.
        """
        self.ao_sair = ao_sair
        self.icone = None
        self._thread = None

    def _gerar_imagem_icone(self) -> Image.Image:
        """
        Gera em tempo de execução a imagem do ícone da bandeja com design Matrix.
        
        Returns:
            Image.Image: Imagem de 64x64 pixels com fundo preto e contornos verdes.
        """
        imagem = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(imagem)
        draw.rectangle([16, 16, 48, 48], outline='#00ff41', width=3)
        draw.text((24, 22), ">", fill='#ff0033')
        return imagem

    def _tratar_clique_sair(self, icon, item):
        """Handler do clique no item de menu para fechamento."""
        if self.ao_sair:
            self.ao_sair()

    def iniciar(self):
        """Inicializa e executa o ícone da bandeja do sistema em uma thread separada."""
        imagem = self._gerar_imagem_icone()
        menu = pystray.Menu(
            pystray.MenuItem("Status: Protegido / Oculto", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair / Fechar", self._tratar_clique_sair)
        )
        self.icone = pystray.Icon("AntiAusente", imagem, "Anti-Ausente Hacker", menu)
        
        self._thread = threading.Thread(target=self.icone.run, daemon=True)
        self._thread.start()

    def parar(self):
        """Remove o ícone da bandeja e finaliza sua execução."""
        if self.icone is not None:
            try:
                self.icone.stop()
            except Exception:
                pass
            self.icone = None
