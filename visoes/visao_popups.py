"""
Módulo de Visão de Popups e Janelas de Diálogo.
Responsável por criar os popups de erro de sistema simulados (Kernel panic, EDR, BitLocker)
e a janela especial de revelação comemorativa da pegadinha ("É PEGADINHA! 🤣").
"""

import random
import winsound
import tkinter as tk
from screeninfo import get_monitors
from configuracao import MAX_POPUPS, NOME_PC, NOME_USUARIO, TEMPO_OCIOSO_ALVO

class VisaoPopups:
    """
    Gerenciador visual de caixas de diálogo simuladas e da janela de revelação.
    
    Responsabilidade:
        Construir janelas Toplevel estilizadas com alertas em vermelho/amarelo,
        garantindo posicionamento randômico que não obstrua o mapa e limitando o número de popups ativos.
    """

    def __init__(self, master_tk: tk.Misc):
        """
        Inicializa o gerenciador de popups.
        
        Args:
            master_tk (tk.Misc): Janela base Tkinter para associação das Toplevels.
        """
        self.master_tk = master_tk
        self.janelas_popups = []

    def disparar_popup_falso(self, ao_clicar_ok=None):
        """
        Gera uma nova janela de erro falso em posição randômica na tela.
        
        Args:
            ao_clicar_ok (Callable | None): Ação executada ao clicar no botão OK (revela a pegadinha).
        """
        mensagens_erro = [
            ("Erro crítico de Kernel", f"Falha de proteção em 0x00007FF7 no processo '{NOME_PC}'."),
            ("Aviso de Segurança", "Acesso não autorizado à webcam e microfone confirmado."),
            ("Windows Defender", f"Múltiplos arquivos de '{NOME_USUARIO}' enviados para servidor externo."),
            ("Atenção Alerta", "Sua chave de recuperação BitLocker foi alterada remotamente.")
        ]
        titulo, texto = random.choice(mensagens_erro)

        try:
            popup = tk.Toplevel(self.master_tk)
            popup.withdraw()
            popup.overrideredirect(True)
            popup.attributes('-topmost', True)

            monitor = get_monitors()[0]
            zona = random.choice(["top", "bottom", "left", "right"])

            # Cálculo de coordenadas para não sobrepor a área do mapa (canto inferior direito)
            if zona == "top":
                px = random.randint(monitor.x + 50, monitor.x + monitor.width - 450)
                py = random.randint(monitor.y + 30, monitor.y + int(monitor.height * 0.15))
            elif zona == "bottom":
                px = random.randint(monitor.x + 50, monitor.x + int(monitor.width * 0.6))
                py = random.randint(monitor.y + int(monitor.height * 0.75), monitor.y + monitor.height - 180)
            elif zona == "left":
                px = random.randint(monitor.x + 30, monitor.x + int(monitor.width * 0.15))
                py = random.randint(monitor.y + 50, monitor.y + monitor.height - 180)
            else:
                px = random.randint(monitor.x + int(monitor.width * 0.78), monitor.x + monitor.width - 450)
                py = random.randint(monitor.y + 50, monitor.y + int(monitor.height * 0.6))

            popup.geometry(f"400x140+{px}+{py}")
            popup.configure(bg='black')

            moldura = tk.Frame(popup, bg='#ff0033', bd=2)
            moldura.pack(fill=tk.BOTH, expand=True)

            conteudo = tk.Frame(moldura, bg='black')
            conteudo.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            frame_tit_pop = tk.Frame(conteudo, bg="black")
            frame_tit_pop.pack(anchor="w", padx=10, pady=(8, 2))

            tk.Label(frame_tit_pop, text="⚠️ ", fg="#ffcc00", bg="black", font=("Consolas", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(frame_tit_pop, text=titulo.upper(), fg="#ff0033", bg="black", font=("Consolas", 10, "bold")).pack(side=tk.LEFT)

            lbl_txt_pop = tk.Label(
                conteudo, text=texto, fg="#00ff41", bg="black", font=("Consolas", 8),
                wraplength=370, justify="left"
            )
            lbl_txt_pop.pack(anchor="w", padx=10, pady=(0, 10))

            btn_ok = tk.Button(
                conteudo, text="OK", bg="#ff0033", fg="white",
                activebackground="#cc0028", activeforeground="white",
                font=("Consolas", 8, "bold"), relief="flat", highlightthickness=0, bd=0,
                command=ao_clicar_ok
            )
            btn_ok.pack(pady=(0, 8))

            popup.deiconify()
            popup.lift()

            try:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass

            self.janelas_popups.append(popup)

            # Mantém apenas a quantidade máxima permitida de janelas
            while len(self.janelas_popups) > MAX_POPUPS:
                p_antigo = self.janelas_popups.pop(0)
                try:
                    p_antigo.destroy()
                except Exception:
                    pass
        except Exception:
            pass

    def exibir_revelacao_pegadinha(self, ao_fechar_tudo):
        """
        Exibe a janela central revelando que se trata de uma pegadinha inofensiva.
        
        Args:
            ao_fechar_tudo (Callable): Callback executado ao clicar no botão de encerramento.
        """
        self.fechar_todos_popups()

        try:
            popup_rev = tk.Toplevel(self.master_tk)
            popup_rev.withdraw()
            popup_rev.overrideredirect(True)
            popup_rev.attributes('-topmost', True)

            monitor = get_monitors()[0]
            w, h = 580, 320
            px = monitor.x + (monitor.width - w) // 2
            py = monitor.y + (monitor.height - h) // 2

            popup_rev.geometry(f"{w}x{h}+{px}+{py}")
            popup_rev.configure(bg='black')

            border = tk.Frame(popup_rev, bg='#00ff41', bd=3)
            border.pack(fill=tk.BOTH, expand=True)

            card = tk.Frame(border, bg='#0d0d0d')
            card.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

            tk.Label(
                card, text="É PEGADINHA! 🤣", fg="#00ff41", bg="#0d0d0d", font=("Consolas", 22, "bold")
            ).pack(pady=(25, 10))

            msg = (
                "Seu PC está 100% seguro!\n\n"
                f"Você ficou {TEMPO_OCIOSO_ALVO} segundos sem mexer no mouse e o modo\n"
                "Anti-Ausente ativou para proteger seu status no Teams/Slack.\n\n"
                "Vá tomar um café e relaxar! ☕"
            )
            tk.Label(
                card, text=msg, fg="white", bg="#0d0d0d", font=("Consolas", 11), justify="center"
            ).pack(pady=10)

            btn_fechar = tk.Button(
                card, text="FECHAR E VOLTAR AO TRABALHO (OU PRESSIONE ESC)",
                bg="#00ff41", fg="black", activebackground="#00cc33", activeforeground="black",
                font=("Consolas", 9, "bold"), relief="flat", padx=15, pady=6,
                command=ao_fechar_tudo
            )
            btn_fechar.pack(pady=(15, 0))

            popup_rev.deiconify()
            popup_rev.lift()
            self.janelas_popups.append(popup_rev)

            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
        except Exception:
            pass

    def fechar_todos_popups(self):
        """Destrói todas as janelas de erro falsas e revelação ativas."""
        for popup in self.janelas_popups:
            try:
                popup.destroy()
            except Exception:
                pass
        self.janelas_popups.clear()
