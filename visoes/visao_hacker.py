"""
Módulo de Visão da Tela Hacker Principal.
Responsável pela criação de janelas sem bordas cobrindo todos os monitores,
gerenciamento do Canvas de tela cheia unificado, textos estilizados do terminal,
efeito glitch de interferência visual e barra de progresso do ataque.
"""

import random
import tkinter as tk
from screeninfo import get_monitors
from configuracao import ARQUIVOS_PARA_DELETAR, TEMPO_CONTADOR_SEG

class VisaoHacker:
    """
    Componente visual que gerencia a tela cheia e os elementos do tema hacker.
    
    Responsabilidade:
        Cobrir todas as telas com janelas pretas transparentes,
        desenhar o terminal de comandos e centralizar os textos dinâmicos.
    """

    def __init__(self, master_tk: tk.Tk):
        """
        Inicializa o gerenciador da tela hacker.
        
        Args:
            master_tk (tk.Tk): Janela base Tkinter.
        """
        self.master_tk = master_tk
        self.janelas_hacker = []
        self.canvas_tela = None
        
        # Identificadores de itens gráficos no Canvas
        self.item_titulo = None
        self.item_sub = None
        self.item_timer = None
        self.item_terminal = None
        self.item_deletando = None
        self.item_barra = None
        
        self.largura_tela = 1920
        self.altura_tela = 1080

    def esta_ativa(self) -> bool:
        """
        Verifica se as janelas de tela cheia estão ativas e abertas.
        
        Returns:
            bool: True se houver janelas hacker ativas.
        """
        return len(self.janelas_hacker) > 0 and self.canvas_tela is not None

    def criar_telas(self) -> tk.Canvas:
        """
        Cria as janelas Toplevel em todos os monitores conectados e inicializa o Canvas principal.
        
        Returns:
            tk.Canvas: Instância do Canvas da tela principal para ancoragem dos demais componentes.
        """
        self.fechar_telas()
        monitores = get_monitors()

        for m in monitores:
            j = tk.Toplevel(self.master_tk)
            j.withdraw()
            j.geometry(f"{m.width}x{m.height}+{m.x}+{m.y}")
            j.overrideredirect(True)
            j.attributes('-topmost', True)
            j.configure(bg='#000000')
            j.config(cursor="none")
            j.deiconify()
            self.janelas_hacker.append(j)

        janela_principal = self.janelas_hacker[0]
        m_principal = monitores[0]
        self.largura_tela = m_principal.width
        self.altura_tela = m_principal.height

        # Canvas unificado de tela cheia sem bordas
        self.canvas_tela = tk.Canvas(
            janela_principal,
            width=self.largura_tela,
            height=self.altura_tela,
            bg='#000000',
            bd=0,
            highlightthickness=0
        )
        self.canvas_tela.pack(fill=tk.BOTH, expand=True)

        centro_x = self.largura_tela // 2

        # 1. Título de Alerta
        self.item_titulo = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.18),
            text="⚠️  FALHA DE SEGURANÇA: SISTEMA COMPROMETIDO  ⚠️",
            fill="#ff0033",
            font=("Consolas", 18, "bold"),
            tags="centro"
        )

        # 2. Subtítulo
        self.item_sub = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.24),
            text="[STATUS: INVASÃO REMOTA EM ANDAMENTO - NÃO DESLIGUE O PC]",
            fill="#ff5555",
            font=("Consolas", 10, "bold"),
            tags="centro"
        )

        # 3. Timer Regressivo
        minutos_ini = TEMPO_CONTADOR_SEG // 60
        segundos_ini = TEMPO_CONTADOR_SEG % 60
        self.item_timer = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.29),
            text=f"TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: {minutos_ini:02d}:{segundos_ini:02d}",
            fill="#ff0033",
            font=("Consolas", 11, "bold"),
            tags="centro"
        )

        # 4. Terminal de Comandos Hacker
        self.item_terminal = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.48),
            text="",
            fill="#00ff41",
            font=("Consolas", 10),
            anchor="center",
            justify="left",
            tags="centro"
        )

        # 5. Rótulo de Arquivos Sendo Apagados
        self.item_deletando = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.69),
            text="[AGUARDANDO VARREDURA DE DISCO...]",
            fill="#ffcc00",
            font=("Consolas", 9, "italic"),
            tags="centro"
        )

        # 6. Barra de Progresso
        self.item_barra = self.canvas_tela.create_text(
            centro_x, int(self.altura_tela * 0.74),
            text="[░░░░░░░░░░░░░░░░░░░░] 0%",
            fill="#00ff41",
            font=("Consolas", 12, "bold"),
            tags="centro"
        )

        return self.canvas_tela

    def atualizar_terminal(self, texto: str):
        """Atualiza o conteúdo de texto do terminal central."""
        if self.canvas_tela and self.canvas_tela.winfo_exists() and self.item_terminal:
            self.canvas_tela.itemconfig(self.item_terminal, text=texto)

    def atualizar_timer(self, minutos: int, segundos: int):
        """Atualiza a contagem regressiva em minutos e segundos."""
        if self.canvas_tela and self.canvas_tela.winfo_exists() and self.item_timer:
            self.canvas_tela.itemconfig(
                self.item_timer,
                text=f"TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: {minutos:02d}:{segundos:02d}"
            )

    def definir_timer_esgotado(self):
        """Exibe mensagem de tempo esgotado."""
        if self.canvas_tela and self.canvas_tela.winfo_exists() and self.item_timer:
            self.canvas_tela.itemconfig(self.item_timer, text="TEMPO ESGOTADO - SISTEMA CRIPTOGRAFADO!")

    def atualizar_barra_progresso(self, progresso: int):
        """Atualiza a barra ASCII de progresso do ataque."""
        if self.canvas_tela and self.canvas_tela.winfo_exists() and self.item_barra:
            blocos = int(progresso / 5)
            barra_str = "[" + "█" * blocos + "░" * (20 - blocos) + f"] {progresso}%"
            self.canvas_tela.itemconfig(self.item_barra, text=barra_str)

    def simular_exclusao_arquivo(self):
        """Escolhe aleatoriamente um arquivo crítico da lista para simular exclusão."""
        if self.canvas_tela and self.canvas_tela.winfo_exists() and self.item_deletando:
            arquivo = random.choice(ARQUIVOS_PARA_DELETAR)
            self.canvas_tela.itemconfig(
                self.item_deletando,
                text=f"[DELETANDO ARQUIVO] {arquivo} ... [APAGADO]"
            )

    def aplicar_glitch(self):
        """Aplica um deslocamento efêmero nos itens centrais para simular instabilidade de vídeo."""
        if self.canvas_tela and self.canvas_tela.winfo_exists():
            if random.random() < 0.40:
                off_x = random.choice([-8, -4, -2, 2, 4, 8])
                off_y = random.choice([-8, -4, -2, 2, 4, 8])
                self.canvas_tela.move("centro", off_x, off_y)
                self.master_tk.after(
                    60,
                    lambda: self.canvas_tela.move("centro", -off_x, -off_y)
                    if self.canvas_tela and self.canvas_tela.winfo_exists() else None
                )

    def alternar_flash_final(self, estado_piscar: bool):
        """Alterna as cores de fundo e texto na fase final de invasão (100%)."""
        if not self.esta_ativa():
            return

        cor_fundo = '#260000' if estado_piscar else '#000000'

        for j in self.janelas_hacker:
            try:
                j.configure(bg=cor_fundo)
            except Exception:
                pass

        if self.canvas_tela and self.canvas_tela.winfo_exists():
            self.canvas_tela.configure(bg=cor_fundo)
            if estado_piscar:
                self.canvas_tela.itemconfig(self.item_titulo, fill='white')
                self.canvas_tela.itemconfig(self.item_timer, fill='yellow')
                self.canvas_tela.itemconfig(self.item_terminal, fill='#ff0033')
                self.canvas_tela.itemconfig(self.item_barra, fill='#ff0033', text="[████████████████████] DADOS ROUBADOS [100%]")
            else:
                self.canvas_tela.itemconfig(self.item_titulo, fill='#ff0033')
                self.canvas_tela.itemconfig(self.item_timer, fill='#ff0033')
                self.canvas_tela.itemconfig(self.item_terminal, fill='#00ff41')
                self.canvas_tela.itemconfig(self.item_barra, fill='#00ff41', text="[████████████████████] SISTEMA BLOQUEADO [100%]")

    def fechar_telas(self):
        """Fecha e destrói todas as janelas de tela cheia ativas."""
        for j in self.janelas_hacker:
            try:
                j.destroy()
            except Exception:
                pass
        self.janelas_hacker.clear()
        self.canvas_tela = None
        self.item_titulo = None
        self.item_sub = None
        self.item_timer = None
        self.item_terminal = None
        self.item_deletando = None
        self.item_barra = None
