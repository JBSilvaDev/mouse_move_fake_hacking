"""
Módulo de Serviço de Captura de Webcam.
Responsável por gerenciar a inicialização da câmera via OpenCV,
leitura dos quadros (frames), conversão para imagens RGB/PIL e aplicação
de efeitos visuais de interferência (glitch cibernético verde).
"""

import random
import cv2
from PIL import Image, ImageOps, ImageTk

class ServicoWebcam:
    """
    Serviço que encapsula o acesso e processamento da Webcam.
    
    Responsabilidade:
        Interagir diretamente com o hardware de vídeo via OpenCV,
        entregando frames já dimensionados e convertidos para o formato PhotoImage do Tkinter.
    """

    def __init__(self, indice_camera: int = 0):
        """
        Inicializa o serviço com o índice da câmera desejada.
        
        Args:
            indice_camera (int): Índice da câmera no sistema operacional (padrão 0).
        """
        self.indice_camera = indice_camera
        self.captura = None

    def esta_aberta(self) -> bool:
        """
        Verifica se a captura de vídeo está ativa e aberta.
        
        Returns:
            bool: True se estiver aberta, False caso contrário.
        """
        return self.captura is not None and self.captura.isOpened()

    def iniciar(self) -> bool:
        """
        Inicializa a captura de vídeo se ainda não estiver ativa.
        
        Returns:
            bool: True se a câmera foi aberta com sucesso.
        """
        if not self.esta_aberta():
            try:
                self.captura = cv2.VideoCapture(self.indice_camera)
                return self.captura.isOpened()
            except Exception:
                self.captura = None
                return False
        return True

    def capturar_frame(self, largura: int = 180, altura: int = 130):
        """
        Captura um quadro da webcam, converte para RGB, redimensiona
        e aplica efeito glitch verde Matrix esporádico.
        
        Args:
            largura (int): Largura desejada do frame em pixels.
            altura (int): Altura desejada do frame em pixels.
            
        Returns:
            ImageTk.PhotoImage | None: Objeto de imagem pronto para exibição no Tkinter ou None se falhar.
        """
        if not self.esta_aberta():
            if not self.iniciar():
                return None

        ret, frame = self.captura.read()
        if not ret:
            return None

        # Conversão de cores BGR (OpenCV) para RGB (Pillow)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_redimensionado = cv2.resize(frame_rgb, (largura, altura))
        img_pil = Image.fromarray(frame_redimensionado)

        # Aplicação de efeito de glitch verde cibernético esporádico (10% de chance)
        if random.random() < 0.10:
            img_pil = ImageOps.colorize(img_pil.convert("L"), black="black", white="#00ff41")

        return ImageTk.PhotoImage(image=img_pil)

    def encerrar(self):
        """Libera os recursos da câmera e encerra o fluxo de captura."""
        if self.captura is not None:
            try:
                self.captura.release()
            except Exception:
                pass
            self.captura = None
