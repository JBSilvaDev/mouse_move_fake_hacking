"""
Módulo de Visão da Bandeja do Sistema (System Tray).
Responsável por criar o ícone com caveirinha hacker na área de notificação do Windows
utilizando Pystray, oferecendo exibição das configurações ativas do sistema
e opções de encerramento seguro do programa.
"""

import threading
import tkinter as tk
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray

from configuracao import (
    INTERVALO_MOVER_MOUSE,
    MAX_POPUPS,
    TEMPO_ATIVAR_WEBCAM,
    TEMPO_CONTADOR_SEG,
    TEMPO_OCIOSO_ALVO,
    USAR_GEOLOCALIZACAO,
    USAR_WEBCAM,
)

class VisaoBandeja:
    """
    Gerenciador visual do ícone na bandeja do sistema com tema Hacker.
    
    Responsabilidade:
        Desenhar o ícone de caveirinha hacker verde Matrix, manter o menu de contexto
        com atalhos e visualização das configurações do sistema, e despachar o encerramento.
    """

    def __init__(self, master_tk: Optional[tk.Misc] = None, ao_sair: Optional[Callable[[], None]] = None):
        """
        Inicializa a visão da bandeja.
        
        Args:
            master_tk (tk.Misc | None): Instância raiz do Tkinter para criação da janela de diálogo.
            ao_sair (Callable | None): Callback disparado ao clicar em 'Sair / Fechar'.
        """
        self.master_tk = master_tk
        self.ao_sair = ao_sair
        self.icone = None
        self._thread = None
        self._janela_config = None

    def _gerar_imagem_icone(self) -> Image.Image:
        """
        Gera em tempo de execução o ícone de caveirinha hacker Matrix (64x64 RGBA).
        
        Returns:
            Image.Image: Imagem com caveira estilizada verde Matrix sobre fundo circular escuro.
        """
        w, h = 64, 64
        imagem = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(imagem)

        # Fundo circular escuro com borda verde Matrix
        draw.ellipse([2, 2, 61, 61], fill=(8, 16, 10, 245), outline='#00ff41', width=2)

        # Crânio superior em verde neon
        draw.ellipse([14, 10, 49, 44], fill='#00ff41', outline='#003300')

        # Mandíbula / dentes
        draw.rectangle([21, 36, 42, 51], fill='#00ff41', outline='#003300')

        # Órbita ocular esquerda (vazio/preto)
        draw.ellipse([19, 23, 29, 36], fill='#000000')

        # Órbita ocular direita (vazio/preto)
        draw.ellipse([34, 23, 44, 36], fill='#000000')

        # Cavidade nasal (triângulo invertido)
        draw.polygon([(32, 38), (29, 44), (35, 44)], fill='#000000')

        # Separação e linhas dos dentes
        draw.line([(21, 46), (42, 46)], fill='#000000', width=1)
        draw.line([(26, 42), (26, 50)], fill='#000000', width=1)
        draw.line([(32, 42), (32, 50)], fill='#000000', width=1)
        draw.line([(37, 42), (37, 50)], fill='#000000', width=1)

        return imagem

    def _abrir_janela_config(self, icon=None, item=None):
        """Despacha a abertura da janela de configurações na thread principal do Tkinter."""
        if self.master_tk:
            self.master_tk.after(0, self.mostrar_janela_configuracoes)

    def mostrar_janela_configuracoes(self):
        """Exibe uma janela flutuante estilizada em tema hacker com as configurações ativas."""
        if self._janela_config and self._janela_config.winfo_exists():
            self._janela_config.lift()
            self._janela_config.focus_force()
            return

        if not self.master_tk:
            return

        win = tk.Toplevel(self.master_tk)
        self._janela_config = win
        win.title("Anti-Ausente Hacker - Configurações")
        win.configure(bg='#0a0a0a')
        win.geometry("520x460")
        win.resizable(False, False)
        win.attributes('-topmost', True)

        # Centraliza na tela
        try:
            from screeninfo import get_monitors
            m = get_monitors()[0]
            px = m.x + (m.width - 520) // 2
            py = m.y + (m.height - 460) // 2
            win.geometry(f"520x460+{px}+{py}")
        except Exception:
            pass

        # Borda externa Matrix
        borda = tk.Frame(win, bg='#00ff41', bd=2)
        borda.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        conteudo = tk.Frame(borda, bg='#0d0d0d')
        conteudo.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Cabeçalho
        frame_cab = tk.Frame(conteudo, bg='#0d0d0d')
        frame_cab.pack(fill=tk.X, padx=16, pady=(16, 10))

        tk.Label(
            frame_cab,
            text="💀 CONFIGURAÇÕES DO SISTEMA",
            fg="#00ff41",
            bg="#0d0d0d",
            font=("Consolas", 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            frame_cab,
            text="[STATUS: MONITORAMENTO ANTI-AUSENTE ATIVO]",
            fg="#888888",
            bg="#0d0d0d",
            font=("Consolas", 8)
        ).pack(anchor="w", pady=(2, 0))

        # Divisor
        tk.Frame(conteudo, bg="#00ff41", height=1).pack(fill=tk.X, padx=16, pady=8)

        # Seção: Tempos e Limites
        frame_tempos = tk.Frame(conteudo, bg='#0d0d0d')
        frame_tempos.pack(fill=tk.X, padx=16, pady=4)

        tk.Label(
            frame_tempos,
            text="[TEMPOS E LIMITES]",
            fg="#ffcc00",
            bg="#0d0d0d",
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", pady=(0, 6))

        configs_tempos = [
            ("TEMPO_OCIOSO_ALVO", f"{TEMPO_OCIOSO_ALVO}s", "Segundos sem mexer para disparar a tela hacker"),
            ("INTERVALO_MOVER_MOUSE", f"{INTERVALO_MOVER_MOUSE}s", "Intervalo para mover o mouse (Anti-Teams)"),
            ("MAX_POPUPS", f"{MAX_POPUPS}", "Limite máximo de janelas de erro falsas"),
            ("TEMPO_CONTADOR_SEG", f"{TEMPO_CONTADOR_SEG}s", f"Contagem regressiva ({TEMPO_CONTADOR_SEG // 60} minutos)"),
            ("TEMPO_ATIVAR_WEBCAM", f"{TEMPO_ATIVAR_WEBCAM}s", "Segundos após invasão para ligar a webcam"),
        ]

        for chave, val, desc in configs_tempos:
            linha = tk.Frame(frame_tempos, bg='#0d0d0d')
            linha.pack(fill=tk.X, pady=2)
            tk.Label(linha, text=f"• {chave}:", fg="#00ff41", bg="#0d0d0d", font=("Consolas", 9, "bold"), width=24, anchor="w").pack(side=tk.LEFT)
            tk.Label(linha, text=f"{val}", fg="#ffffff", bg="#0d0d0d", font=("Consolas", 9, "bold"), width=8, anchor="w").pack(side=tk.LEFT)
            tk.Label(linha, text=f"// {desc}", fg="#666666", bg="#0d0d0d", font=("Consolas", 8), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Divisor
        tk.Frame(conteudo, bg="#222222", height=1).pack(fill=tk.X, padx=16, pady=8)

        # Seção: Recursos e Flags
        frame_flags = tk.Frame(conteudo, bg='#0d0d0d')
        frame_flags.pack(fill=tk.X, padx=16, pady=4)

        tk.Label(
            frame_flags,
            text="[RECURSOS E FLAGS]",
            fg="#ffcc00",
            bg="#0d0d0d",
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", pady=(0, 6))

        configs_flags = [
            ("USAR_WEBCAM", "True" if USAR_WEBCAM else "False", "Exibe streaming e gravação da webcam"),
            ("USAR_GEOLOCALIZACAO", "True" if USAR_GEOLOCALIZACAO else "False", "Busca localização e exibe o Live Map"),
        ]

        for chave, val, desc in configs_flags:
            linha = tk.Frame(frame_flags, bg='#0d0d0d')
            linha.pack(fill=tk.X, pady=2)
            tk.Label(linha, text=f"• {chave}:", fg="#00ff41", bg="#0d0d0d", font=("Consolas", 9, "bold"), width=24, anchor="w").pack(side=tk.LEFT)
            cor_val = "#00ff41" if val == "True" else "#ff5555"
            tk.Label(linha, text=f"{val}", fg=cor_val, bg="#0d0d0d", font=("Consolas", 9, "bold"), width=8, anchor="w").pack(side=tk.LEFT)
            tk.Label(linha, text=f"// {desc}", fg="#666666", bg="#0d0d0d", font=("Consolas", 8), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botão Fechar
        btn_fechar = tk.Button(
            conteudo,
            text="FECHAR",
            bg="#00ff41",
            fg="#000000",
            activebackground="#00cc33",
            activeforeground="#000000",
            font=("Consolas", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            command=win.destroy
        )
        btn_fechar.pack(pady=(15, 10))

    def _tratar_clique_sair(self, icon, item):
        """Handler do clique no item de menu para fechamento do programa."""
        if self.ao_sair:
            self.ao_sair()

    def iniciar(self):
        """Inicializa e executa o ícone da bandeja do sistema em uma thread separada."""
        imagem = self._gerar_imagem_icone()

        submenu_configs = pystray.Menu(
            pystray.MenuItem(f"Tempo Ocioso: {TEMPO_OCIOSO_ALVO}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Intervalo Mouse: {INTERVALO_MOVER_MOUSE}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Max Popups: {MAX_POPUPS}", lambda: None, enabled=False),
            pystray.MenuItem(f"Contador: {TEMPO_CONTADOR_SEG}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Timer Webcam: {TEMPO_ATIVAR_WEBCAM}s", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Webcam: {'Ativada' if USAR_WEBCAM else 'Desativada'}", lambda: None, enabled=False),
            pystray.MenuItem(f"Geolocalização: {'Ativada' if USAR_GEOLOCALIZACAO else 'Desativada'}", lambda: None, enabled=False),
        )

        menu = pystray.Menu(
            pystray.MenuItem("💀 Anti-Ausente Hacker (Ativo)", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Ver Configurações", self._abrir_janela_config),
            pystray.MenuItem("📋 Resumo Rápido", submenu_configs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair / Fechar", self._tratar_clique_sair)
        )
        self.icone = pystray.Icon("AntiAusente", imagem, "Anti-Ausente Hacker", menu)

        self._thread = threading.Thread(target=self.icone.run, daemon=True)
        self._thread.start()

    def parar(self):
        """Remove o ícone da bandeja e finaliza sua execução."""
        if self._janela_config and self._janela_config.winfo_exists():
            try:
                self._janela_config.destroy()
            except Exception:
                pass
            self._janela_config = None

        if self.icone is not None:
            try:
                self.icone.stop()
            except Exception:
                pass
            self.icone = None
