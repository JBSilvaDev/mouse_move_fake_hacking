"""
Módulo de Visão do Feed da Webcam.
Responsável pela interface do feed da câmera na tela cheia,
incluindo moldura de segurança, cabeçalho de status da gravação
e renderização contínua dos quadros de vídeo capturados.
"""

import tkinter as tk
from configuracao import TEMPO_ATIVAR_WEBCAM

class VisaoWebcam:
    """
    Componente visual responsável pela exibição da moldura e streaming da webcam.
    
    Responsabilidade:
        Construir o card visual de transmissão, atualizar rótulos de contagem regressiva
        e fixar os quadros de vídeo na interface Tkinter.
    """

    def __init__(self):
        """Inicializa os ponteiros para os elementos visuais do componente."""
        self.frame_container = None
        self.lbl_cabecalho = None
        self.lbl_video = None

    def criar_elementos(self, parent_canvas: tk.Canvas, pos_x: int, pos_y: int):
        """
        Cria o container e widgets da webcam e os posiciona sobre o Canvas.
        
        Args:
            parent_canvas (tk.Canvas): Canvas de tela cheia onde o frame será ancorado.
            pos_x (int): Coordenada horizontal de ancoragem.
            pos_y (int): Coordenada vertical de ancoragem.
        """
        self.frame_container = tk.Frame(
            parent_canvas,
            bg='#000000',
            highlightbackground='#ff0033',
            highlightthickness=2
        )
        parent_canvas.create_window(pos_x, pos_y, anchor="nw", window=self.frame_container)

        self.lbl_cabecalho = tk.Label(
            self.frame_container,
            text=f"⏳ WEBCAM (INICIANDO EM {TEMPO_ATIVAR_WEBCAM}s...)",
            fg="#ffcc00",
            bg="#000000",
            font=("Consolas", 7, "bold")
        )
        self.lbl_cabecalho.pack(anchor="w", padx=3, pady=(2, 0))

        self.lbl_video = tk.Label(
            self.frame_container,
            text="\n  [ CONECTANDO SERVIDOR DE STREAMING ]  \n  [ AGUARDANDO LIBERAÇÃO DA CÂMERA ]  \n",
            fg="#ff5555",
            bg="#000000",
            font=("Consolas", 8)
        )
        self.lbl_video.pack(padx=3, pady=3)

    def definir_status_transmitindo(self):
        """Atualiza o texto e estilo do cabeçalho quando a transmissão ao vivo for iniciada."""
        if self.lbl_cabecalho and self.lbl_cabecalho.winfo_exists():
            self.lbl_cabecalho.config(text="🔴 LIVE STREAMING (TRANSMITINDO)", fg="#ff0033")

    def atualizar_frame_video(self, img_tk):
        """
        Exibe uma nova imagem no rótulo de vídeo.
        
        Args:
            img_tk (ImageTk.PhotoImage): Imagem convertida para o Tkinter.
        """
        if self.lbl_video and self.lbl_video.winfo_exists() and img_tk:
            self.lbl_video.img_tk = img_tk
            self.lbl_video.config(image=img_tk)

    def alterar_cor_fundo(self, cor: str):
        """
        Ajusta a cor de fundo do container durante os efeitos de alarme ou flash.
        
        Args:
            cor (str): Código hexadecimal da cor (ex: '#260000' ou '#000000').
        """
        if self.frame_container and self.frame_container.winfo_exists():
            self.frame_container.configure(bg=cor)
            if self.lbl_cabecalho and self.lbl_cabecalho.winfo_exists():
                self.lbl_cabecalho.configure(bg=cor)
            if self.lbl_video and self.lbl_video.winfo_exists() and not hasattr(self.lbl_video, 'img_tk'):
                self.lbl_video.configure(bg=cor)

    def destruir(self):
        """Destrói os widgets associados à webcam de forma limpa."""
        if self.frame_container and self.frame_container.winfo_exists():
            try:
                self.frame_container.destroy()
            except Exception:
                pass
        self.frame_container = None
        self.lbl_cabecalho = None
        self.lbl_video = None
