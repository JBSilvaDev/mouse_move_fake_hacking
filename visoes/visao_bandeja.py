"""
Módulo de Visão da Bandeja do Sistema (System Tray).
Responsável por criar o ícone com caveirinha hacker na área de notificação do Windows
utilizando Pystray, oferecendo exibição e EDIÇÃO EM TEMPO REAL das configurações ativas
do sistema sem necessidade de reiniciar a aplicação.
"""

import threading
import tkinter as tk
from typing import Callable, Optional
from PIL import Image, ImageDraw, ImageTk
import pystray
import configuracao

class VisaoBandeja:
    """
    Gerenciador visual do ícone na bandeja do sistema com tema Hacker.
    
    Responsabilidade:
        Desenhar o ícone de caveirinha hacker verde Matrix, manter o menu de contexto,
        oferecer interface de edição em tempo real das configurações do sistema com persistência
        e despachar o encerramento seguro.
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
        self._icone_tk = None

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

    def _atualizar_menu_bandeja(self):
        """Atualiza dinamicamente os valores exibidos no menu da bandeja após edição."""
        if not self.icone:
            return

        submenu_configs = pystray.Menu(
            pystray.MenuItem(f"Tempo Ocioso: {configuracao.TEMPO_OCIOSO_ALVO}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Intervalo Anti-Ausente: {configuracao.INTERVALO_MOVER_MOUSE}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Max Popups: {configuracao.MAX_POPUPS}", lambda: None, enabled=False),
            pystray.MenuItem(f"Contador: {configuracao.TEMPO_CONTADOR_SEG}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Timer Webcam: {configuracao.TEMPO_ATIVAR_WEBCAM}s", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Tela Hacker: {'Ativada' if configuracao.ATIVAR_TELA_HACKER else 'Desativada'}", lambda: None, enabled=False),
            pystray.MenuItem(f"Webcam: {'Ativada' if configuracao.USAR_WEBCAM else 'Desativada'}", lambda: None, enabled=False),
            pystray.MenuItem(f"Geolocalização: {'Ativada' if configuracao.USAR_GEOLOCALIZACAO else 'Desativada'}", lambda: None, enabled=False),
        )

        novo_menu = pystray.Menu(
            pystray.MenuItem("💀 Anti-Ausente Hacker (Ativo)", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Ver / Editar Configurações", self._abrir_janela_config),
            pystray.MenuItem("📋 Resumo Rápido", submenu_configs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair / Fechar", self._tratar_clique_sair)
        )
        self.icone.menu = novo_menu

    def mostrar_janela_configuracoes(self):
        """
        Exibe uma janela flutuante interativa com tema Hacker permitindo visualizar
        e editar todos os parâmetros de configuração diretamente com aplicação em tempo real.
        """
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
        win.geometry("540x610")
        win.resizable(False, False)
        win.attributes('-topmost', True)
        win.bind("<Escape>", lambda e: win.destroy())

        # Aplica o mesmo ícone de caveirinha na janela do Tkinter
        try:
            self._icone_tk = ImageTk.PhotoImage(self._gerar_imagem_icone(), master=win)
            win.iconphoto(False, self._icone_tk)
        except Exception:
            pass

        # Centraliza na tela
        try:
            from screeninfo import get_monitors
            m = get_monitors()[0]
            px = m.x + (m.width - 540) // 2
            py = m.y + (m.height - 610) // 2
            win.geometry(f"540x610+{px}+{py}")
        except Exception:
            pass

        # Borda externa Matrix
        borda = tk.Frame(win, bg='#00ff41', bd=2)
        borda.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        conteudo = tk.Frame(borda, bg='#0d0d0d')
        conteudo.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Cabeçalho
        frame_cab = tk.Frame(conteudo, bg='#0d0d0d')
        frame_cab.pack(fill=tk.X, padx=16, pady=(14, 6))

        tk.Label(
            frame_cab,
            text="💀 PAINEL DE CONTROLE HACKER",
            fg="#00ff41",
            bg="#0d0d0d",
            font=("Consolas", 13, "bold")
        ).pack(anchor="w")

        tk.Label(
            frame_cab,
            text="[EDIÇÃO EM TEMPO REAL - ALTERE E CLIQUE EM SALVAR]",
            fg="#888888",
            bg="#0d0d0d",
            font=("Consolas", 8)
        ).pack(anchor="w", pady=(2, 0))

        # Divisor
        tk.Frame(conteudo, bg="#00ff41", height=1).pack(fill=tk.X, padx=16, pady=6)

        entradas = {}
        labels_dinamicos = {}

        # =========================================================================
        # SEÇÃO 1: ANTI-AUSENTE & SISTEMA (Sempre ativos)
        # =========================================================================
        frame_sistema = tk.Frame(conteudo, bg='#0d0d0d')
        frame_sistema.pack(fill=tk.X, padx=16, pady=2)

        tk.Label(
            frame_sistema,
            text="[ANTI-AUSENTE & SISTEMA]",
            fg="#ffcc00",
            bg="#0d0d0d",
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        campos_sistema = [
            ("INTERVALO_MOVER_MOUSE", str(configuracao.INTERVALO_MOVER_MOUSE), "Intervalo anti-ausente (F15 + cursor)"),
            ("TEMPO_OCIOSO_ALVO", str(configuracao.TEMPO_OCIOSO_ALVO), "Segundos ociosos p/ disparo"),
        ]

        for chave, val_ini, desc in campos_sistema:
            linha = tk.Frame(frame_sistema, bg='#0d0d0d')
            linha.pack(fill=tk.X, pady=2)

            tk.Label(
                linha, text=f"• {chave}:", fg="#00ff41", bg="#0d0d0d",
                font=("Consolas", 9, "bold"), width=24, anchor="w"
            ).pack(side=tk.LEFT)

            ent = tk.Entry(
                linha, bg='#1a1a1a', fg='#ffffff', insertbackground='#00ff41',
                font=("Consolas", 9, "bold"), width=7, justify="center", bd=1, relief="solid",
                highlightcolor="#00ff41", highlightthickness=1
            )
            ent.insert(0, val_ini)
            ent.pack(side=tk.LEFT, padx=(0, 10))
            entradas[chave] = ent

            tk.Label(
                linha, text=f"// {desc}", fg="#666666", bg="#0d0d0d",
                font=("Consolas", 8), anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Divisor
        tk.Frame(conteudo, bg="#222222", height=1).pack(fill=tk.X, padx=16, pady=6)

        # =========================================================================
        # SEÇÃO 2: SIMULAÇÃO TELA HACKER (Controlada pelo interruptor mestre)
        # =========================================================================
        frame_hacker = tk.Frame(conteudo, bg='#0d0d0d')
        frame_hacker.pack(fill=tk.X, padx=16, pady=2)

        tk.Label(
            frame_hacker,
            text="[SIMULAÇÃO TELA HACKER]",
            fg="#ffcc00",
            bg="#0d0d0d",
            font=("Consolas", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        var_tela_hacker = tk.BooleanVar(value=bool(configuracao.ATIVAR_TELA_HACKER))
        var_geo = tk.BooleanVar(value=bool(configuracao.USAR_GEOLOCALIZACAO))
        var_webcam = tk.BooleanVar(value=bool(configuracao.USAR_WEBCAM))

        # 1. Interruptor Mestre da Tela Hacker
        linha_mestre = tk.Frame(frame_hacker, bg='#0d0d0d')
        linha_mestre.pack(fill=tk.X, pady=2)
        tk.Label(
            linha_mestre, text="• ATIVAR_TELA_HACKER:", fg="#00ff41", bg="#0d0d0d",
            font=("Consolas", 9, "bold"), width=24, anchor="w"
        ).pack(side=tk.LEFT)
        cb_hacker = tk.Checkbutton(
            linha_mestre, text="", variable=var_tela_hacker,
            bg='#0d0d0d', fg='#00ff41', selectcolor='#1a1a1a', activebackground='#0d0d0d',
            activeforeground='#00ff41', bd=0, highlightthickness=0
        )
        cb_hacker.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(
            linha_mestre, text="// Ativa simulação visual de invasão", fg="#888888",
            bg="#0d0d0d", font=("Consolas", 8, "italic"), anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 2. Parâmetros visuais gerais (Contador e Popups)
        campos_hacker_nums = [
            ("TEMPO_CONTADOR_SEG", str(configuracao.TEMPO_CONTADOR_SEG), "Contagem regressiva (segundos)"),
            ("MAX_POPUPS", str(configuracao.MAX_POPUPS), "Limite máximo de popups falsos"),
        ]
        for chave, val_ini, desc in campos_hacker_nums:
            linha = tk.Frame(frame_hacker, bg='#0d0d0d')
            linha.pack(fill=tk.X, pady=2)

            lbl_chave = tk.Label(
                linha, text=f"• {chave}:", fg="#00ff41", bg="#0d0d0d",
                font=("Consolas", 9, "bold"), width=24, anchor="w"
            )
            lbl_chave.pack(side=tk.LEFT)

            ent = tk.Entry(
                linha, bg='#1a1a1a', fg='#ffffff', insertbackground='#00ff41',
                font=("Consolas", 9, "bold"), width=7, justify="center", bd=1, relief="solid",
                highlightcolor="#00ff41", highlightthickness=1
            )
            ent.insert(0, val_ini)
            ent.pack(side=tk.LEFT, padx=(0, 10))
            entradas[chave] = ent

            lbl_desc = tk.Label(
                linha, text=f"// {desc}", fg="#666666", bg="#0d0d0d",
                font=("Consolas", 8), anchor="w"
            )
            lbl_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)

            labels_dinamicos[chave] = (lbl_chave, lbl_desc)

        # 3. Checkbox Geolocalização
        linha_geo = tk.Frame(frame_hacker, bg='#0d0d0d')
        linha_geo.pack(fill=tk.X, pady=2)
        lbl_geo_chave = tk.Label(
            linha_geo, text="• USAR_GEOLOCALIZACAO:", fg="#00ff41", bg="#0d0d0d",
            font=("Consolas", 9, "bold"), width=24, anchor="w"
        )
        lbl_geo_chave.pack(side=tk.LEFT)
        cb_geo = tk.Checkbutton(
            linha_geo, text="", variable=var_geo,
            bg='#0d0d0d', fg='#00ff41', selectcolor='#1a1a1a', activebackground='#0d0d0d',
            activeforeground='#00ff41', bd=0, highlightthickness=0
        )
        cb_geo.pack(side=tk.LEFT, padx=(0, 10))
        lbl_geo_desc = tk.Label(
            linha_geo, text="// Exibe mapa mundi de ameaças", fg="#666666",
            bg="#0d0d0d", font=("Consolas", 8), anchor="w"
        )
        lbl_geo_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 4. Checkbox Webcam
        linha_webcam = tk.Frame(frame_hacker, bg='#0d0d0d')
        linha_webcam.pack(fill=tk.X, pady=2)
        lbl_webcam_chave = tk.Label(
            linha_webcam, text="• USAR_WEBCAM:", fg="#00ff41", bg="#0d0d0d",
            font=("Consolas", 9, "bold"), width=24, anchor="w"
        )
        lbl_webcam_chave.pack(side=tk.LEFT)
        cb_webcam = tk.Checkbutton(
            linha_webcam, text="", variable=var_webcam,
            bg='#0d0d0d', fg='#00ff41', selectcolor='#1a1a1a', activebackground='#0d0d0d',
            activeforeground='#00ff41', bd=0, highlightthickness=0
        )
        cb_webcam.pack(side=tk.LEFT, padx=(0, 10))
        lbl_webcam_desc = tk.Label(
            linha_webcam, text="// Ativa simulação de webcam", fg="#666666",
            bg="#0d0d0d", font=("Consolas", 8), anchor="w"
        )
        lbl_webcam_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 5. Sub-opção: Tempo para Ativar Webcam (Indentada visualmente sob USAR_WEBCAM)
        linha_tempo_cam = tk.Frame(frame_hacker, bg='#0d0d0d')
        linha_tempo_cam.pack(fill=tk.X, pady=(2, 4))
        lbl_cam_tempo_chave = tk.Label(
            linha_tempo_cam, text="  ↳ TEMPO_ATIVAR_WEBCAM:", fg="#00ff41", bg="#0d0d0d",
            font=("Consolas", 9, "bold"), width=24, anchor="w"
        )
        lbl_cam_tempo_chave.pack(side=tk.LEFT)

        ent_cam_tempo = tk.Entry(
            linha_tempo_cam, bg='#1a1a1a', fg='#ffffff', insertbackground='#00ff41',
            font=("Consolas", 9, "bold"), width=7, justify="center", bd=1, relief="solid",
            highlightcolor="#00ff41", highlightthickness=1
        )
        ent_cam_tempo.insert(0, str(configuracao.TEMPO_ATIVAR_WEBCAM))
        ent_cam_tempo.pack(side=tk.LEFT, padx=(0, 10))
        entradas["TEMPO_ATIVAR_WEBCAM"] = ent_cam_tempo

        lbl_cam_tempo_desc = tk.Label(
            linha_tempo_cam, text="// Segundos de invasão p/ ligar webcam", fg="#666666",
            bg="#0d0d0d", font=("Consolas", 8), anchor="w"
        )
        lbl_cam_tempo_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # =========================================================================
        # REATIVIDADE DINÂMICA ENTRE AS OPÇÕES
        # =========================================================================
        def atualizar_estado_hacker():
            """Habilita ou desabilita as opções secundárias com base no estado da tela hacker e da webcam."""
            hacker_ativo = bool(var_tela_hacker.get())
            estado_hacker = 'normal' if hacker_ativo else 'disabled'
            estado_cb = 'normal' if hacker_ativo else 'disabled'

            if not hacker_ativo:
                var_webcam.set(False)
                var_geo.set(False)

            # Opções numéricas que dependem da tela hacker
            for chave in ["TEMPO_CONTADOR_SEG", "MAX_POPUPS"]:
                if chave in entradas:
                    entradas[chave].config(
                        state=estado_hacker,
                        disabledbackground='#111111',
                        disabledforeground='#444444'
                    )
                if chave in labels_dinamicos:
                    lbl_ch, lbl_ds = labels_dinamicos[chave]
                    lbl_ch.config(fg="#00ff41" if hacker_ativo else "#444444")
                    lbl_ds.config(fg="#666666" if hacker_ativo else "#333333")

            # Checkboxes de flags da tela hacker
            cb_geo.config(state=estado_cb)
            lbl_geo_chave.config(fg="#00ff41" if hacker_ativo else "#444444")
            lbl_geo_desc.config(fg="#666666" if hacker_ativo else "#333333")

            cb_webcam.config(state=estado_cb)
            lbl_webcam_chave.config(fg="#00ff41" if hacker_ativo else "#444444")
            lbl_webcam_desc.config(fg="#666666" if hacker_ativo else "#333333")

            # O tempo da webcam depende de AMBOS: tela hacker ativa E webcam marcada
            webcam_ativa = hacker_ativo and bool(var_webcam.get())
            estado_tempo_cam = 'normal' if webcam_ativa else 'disabled'

            ent_cam_tempo.config(
                state=estado_tempo_cam,
                disabledbackground='#111111',
                disabledforeground='#444444'
            )
            lbl_cam_tempo_chave.config(fg="#00ff41" if webcam_ativa else "#444444")
            lbl_cam_tempo_desc.config(fg="#666666" if webcam_ativa else "#333333")

        cb_hacker.config(command=atualizar_estado_hacker)
        cb_webcam.config(command=atualizar_estado_hacker)
        atualizar_estado_hacker()

        # Divisor
        tk.Frame(conteudo, bg="#222222", height=1).pack(fill=tk.X, padx=16, pady=6)

        # Rótulo de status da operação
        lbl_status = tk.Label(
            conteudo, text="", fg="#00ff41", bg="#0d0d0d", font=("Consolas", 9, "bold")
        )
        lbl_status.pack(pady=(2, 4))

        def salvar_alteracoes():
            """Valida, aplica em memória e salva no arquivo as novas configurações."""
            try:
                novos_valores = {
                    "TEMPO_OCIOSO_ALVO": int(entradas["TEMPO_OCIOSO_ALVO"].get().strip()),
                    "INTERVALO_MOVER_MOUSE": int(entradas["INTERVALO_MOVER_MOUSE"].get().strip()),
                    "MAX_POPUPS": int(entradas["MAX_POPUPS"].get().strip()),
                    "TEMPO_CONTADOR_SEG": int(entradas["TEMPO_CONTADOR_SEG"].get().strip()),
                    "TEMPO_ATIVAR_WEBCAM": int(entradas["TEMPO_ATIVAR_WEBCAM"].get().strip()),
                    "ATIVAR_TELA_HACKER": bool(var_tela_hacker.get()),
                    "USAR_WEBCAM": bool(var_webcam.get()),
                    "USAR_GEOLOCALIZACAO": bool(var_geo.get()),
                }

                # Validação básica de valores positivos
                for k, v in novos_valores.items():
                    if isinstance(v, int) and v < 0:
                        lbl_status.config(text=f"⚠️ {k} deve ser positivo!", fg="#ff0033")
                        return

                sucesso = configuracao.salvar_configuracoes_no_arquivo(novos_valores)
                if sucesso:
                    self._atualizar_menu_bandeja()
                    win.destroy()
                else:
                    lbl_status.config(text="⚠️ Erro ao salvar no disco, mas aplicado em memória.", fg="#ffcc00")
            except ValueError:
                lbl_status.config(text="⚠️ Erro: Digite apenas números inteiros válidos!", fg="#ff0033")

        # Botões de Ação
        frame_botoes = tk.Frame(conteudo, bg='#0d0d0d')
        frame_botoes.pack(pady=(4, 10))

        btn_salvar = tk.Button(
            frame_botoes,
            text="💾 SALVAR CONFIGURAÇÕES",
            bg="#00ff41",
            fg="#000000",
            activebackground="#00cc33",
            activeforeground="#000000",
            font=("Consolas", 9, "bold"),
            relief="flat",
            padx=14,
            pady=5,
            command=salvar_alteracoes
        )
        btn_salvar.pack(side=tk.LEFT, padx=6)

        btn_fechar = tk.Button(
            frame_botoes,
            text="FECHAR",
            bg="#222222",
            fg="#ffffff",
            activebackground="#333333",
            activeforeground="#ffffff",
            font=("Consolas", 9, "bold"),
            relief="flat",
            padx=14,
            pady=5,
            command=win.destroy
        )
        btn_fechar.pack(side=tk.LEFT, padx=6)

    def _tratar_clique_sair(self, icon, item):
        """Handler do clique no item de menu para fechamento do programa."""
        if self.ao_sair:
            self.ao_sair()

    def iniciar(self):
        """Inicializa e executa o ícone da bandeja do sistema em uma thread separada."""
        imagem = self._gerar_imagem_icone()

        submenu_configs = pystray.Menu(
            pystray.MenuItem(f"Tempo Ocioso: {configuracao.TEMPO_OCIOSO_ALVO}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Intervalo Anti-Ausente: {configuracao.INTERVALO_MOVER_MOUSE}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Max Popups: {configuracao.MAX_POPUPS}", lambda: None, enabled=False),
            pystray.MenuItem(f"Contador: {configuracao.TEMPO_CONTADOR_SEG}s", lambda: None, enabled=False),
            pystray.MenuItem(f"Timer Webcam: {configuracao.TEMPO_ATIVAR_WEBCAM}s", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Tela Hacker: {'Ativada' if configuracao.ATIVAR_TELA_HACKER else 'Desativada'}", lambda: None, enabled=False),
            pystray.MenuItem(f"Webcam: {'Ativada' if configuracao.USAR_WEBCAM else 'Desativada'}", lambda: None, enabled=False),
            pystray.MenuItem(f"Geolocalização: {'Ativada' if configuracao.USAR_GEOLOCALIZACAO else 'Desativada'}", lambda: None, enabled=False),
        )

        menu = pystray.Menu(
            pystray.MenuItem("💀 Anti-Ausente Hacker (Ativo)", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Ver / Editar Configurações", self._abrir_janela_config),
            pystray.MenuItem("📋 Resumo Rápido", submenu_configs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair / Fechar", self._tratar_clique_sair)
        )
        self.icone = pystray.Icon("AntiAusente", imagem, "Anti-Ausente Hacker", menu)

        self._thread = threading.Thread(target=self.icone.run, daemon=True)
        self._thread.start()

    def parar(self):
        """Remove o ícone da bandeja e finaliza sua execução."""
        def _destruir_janela():
            if self._janela_config and self._janela_config.winfo_exists():
                try:
                    self._janela_config.destroy()
                except Exception:
                    pass
                self._janela_config = None

        if self.master_tk:
            try:
                self.master_tk.after(0, _destruir_janela)
            except Exception:
                _destruir_janela()
        else:
            _destruir_janela()

        if self.icone is not None:
            try:
                self.icone.stop()
            except Exception:
                pass
            self.icone = None
