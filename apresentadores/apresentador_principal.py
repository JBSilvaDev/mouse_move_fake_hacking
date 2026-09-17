"""
Módulo do Apresentador Principal (Presenter) da Arquitetura MVP.
Responsável por orquestrar a lógica de negócios, interações de entrada,
ciclo de vida dos componentes visuais, agendamento de temporizadores no Tkinter
e integração entre Modelos e Visões.
"""

import random
import time
import winsound
import tkinter as tk
from datetime import datetime

import configuracao
from configuracao import (
    COMANDOS_HACKER,
    MAPA_ALTURA,
    MAPA_LARGURA,
    NOME_PC,
    NOME_USUARIO,
)
from modelos.estado_aplicacao import EstadoAplicacao
from modelos.monitor_entrada import MonitorEntrada
from modelos.servico_geolocalizacao import ServicoGeolocalizacao
from modelos.servico_mouse import ServicoMouse
from modelos.servico_webcam import ServicoWebcam
from visoes.visao_bandeja import VisaoBandeja
from visoes.visao_hacker import VisaoHacker
from visoes.visao_mapa import VisaoMapa
from visoes.visao_popups import VisaoPopups
from visoes.visao_webcam import VisaoWebcam

def log(mensagem: str, categoria: str = "INFO"):
    """
    Função utilitária para registro de logs formatados no console.
    
    Args:
        mensagem (str): Mensagem a ser registrada.
        categoria (str): Tag descritiva da operação.
    """
    hora_atual = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora_atual}] [{categoria}] {mensagem}")

class ApresentadorPrincipal:
    """
    Apresentador central da aplicação Anti-Ausente Hacker.
    
    Responsabilidade:
        Conectar e mediar o fluxo de informações entre os modelos de dados e serviços
        (mouse, teclado, geolocalização, webcam) e os elementos de interface gráfica
        (tela cheia hacker, mapa tático, popups e ícone da bandeja).
    """

    def __init__(self, master_tk: tk.Tk):
        """
        Inicializa o apresentador com todos os seus modelos, visões e variáveis de loop.
        
        Args:
            master_tk (tk.Tk): Janela raiz do Tkinter.
        """
        self.root = master_tk

        # --- MODELOS E SERVIÇOS ---
        self.estado = EstadoAplicacao()
        self.servico_geo = ServicoGeolocalizacao()
        self.servico_webcam = ServicoWebcam()
        self.servico_mouse = ServicoMouse()
        self.monitor_entrada = MonitorEntrada(
            ao_interagir=self.ao_interagir_usuario,
            ao_pressionar_esc=self.ao_pressionar_esc
        )

        # --- VISÕES (VIEWS) ---
        self.visao_hacker = VisaoHacker(self.root)
        self.visao_mapa = VisaoMapa(MAPA_LARGURA, MAPA_ALTURA)
        self.visao_webcam = VisaoWebcam()
        self.visao_popups = VisaoPopups(self.root)
        self.visao_bandeja = VisaoBandeja(master_tk=self.root, ao_sair=self.encerrar_aplicacao)

        # --- IDENTIFICADORES DE LOOPS DO TKINTER ---
        self._loop_sistema_id = None
        self._loop_texto_id = None
        self._loop_barra_id = None
        self._loop_popups_id = None
        self._loop_timer_id = None
        self._loop_glitch_id = None
        self._loop_webcam_id = None
        self._loop_deletar_id = None
        self._loop_mapa_id = None
        self._timer_webcam_id = None

    def inicializar(self):
        """Prepara o ambiente, carrega recursos e inicia os loops de serviço."""
        log("Iniciando monitoramento de ociosidade...", "INÍCIO")
        log(f"Host: {NOME_PC} | Usuário: {NOME_USUARIO}", "SISTEMA")

        # Inicia monitoramento de entrada
        self.monitor_entrada.iniciar()

        # Inicia ícone da bandeja
        self.visao_bandeja.iniciar()

        # Pré-carrega dados do mapa e imagem base para evitar lag na transição
        if configuracao.USAR_GEOLOCALIZACAO:
            self._preparar_mapa_global()

        # Inicia verificação periódica de inatividade e movimentação do cursor
        self._agendar_verificacao_sistema()

    def _preparar_mapa_global(self):
        """Carrega os dados de geolocalização e gera a imagem gráfica do mapa em cache."""
        log("Preparando dados de geolocalização e Cyber Attack Map...", "GEO")
        self.estado.dados_geolocalizacao = self.servico_geo.obter_geolocalizacao_completa()
        self.visao_mapa.carregar_imagem_tk(self.root)
        cidade = self.estado.dados_geolocalizacao.get('city')
        ip = self.estado.dados_geolocalizacao.get('query')
        log(f"Cyber Threat Map pronto. Alvo travado em: {cidade} ({ip})", "GEO")

    def _agendar_verificacao_sistema(self):
        """Agenda a execução do método de verificação periódica do sistema."""
        self._loop_sistema_id = self.root.after(500, self.verificar_sistema)

    def verificar_sistema(self):
        """
        Ciclo de verificação periódica do sistema:
        1. Avalia se o usuário atingiu o tempo ocioso para disparar a tela hacker.
        2. Avalia se deve movimentar o mouse para manter o Teams/Slack ativo.
        """
        tempo_inativo = self.estado.tempo_sem_atividade()

        # Dispara a tela hacker se o tempo ocioso for atingido e ela não estiver ativa
        if tempo_inativo >= configuracao.TEMPO_OCIOSO_ALVO and not self.visao_hacker.esta_ativa():
            log(f"Inatividade de {int(tempo_inativo)}s. Ativando Tela Hacker...", "ALERTA")
            self.ativar_modo_hacker()

        # Movimentação preventiva periódica do mouse
        if self.estado.tempo_desde_ultimo_movimento_mouse() >= configuracao.INTERVALO_MOVER_MOUSE:
            self.monitor_entrada.ignorar_eventos_script = True
            novo_x, novo_y = self.servico_mouse.mover_preventivamente()
            self.monitor_entrada.ignorar_eventos_script = False
            self.estado.registrar_movimento_preventivo()
            log(f"Mouse ajustado preventivamente para ({novo_x}, {novo_y})", "MONITOR")

        self._agendar_verificacao_sistema()

    def ativar_modo_hacker(self):
        """Cria e ativa a interface visual da invasão simulada em tela cheia."""
        self.estado.resetar_sessao_hacker()
        self.estado.tela_hacker_ativa = True

        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass

        # Constrói o Canvas de tela cheia unificado
        canvas = self.visao_hacker.criar_telas()
        tela_w = self.visao_hacker.largura_tela
        tela_h = self.visao_hacker.altura_tela

        # Constrói o widget da Webcam no canto superior esquerdo
        if configuracao.USAR_WEBCAM:
            pos_wx = int(tela_w * 0.03)
            pos_wy = int(tela_h * 0.03)
            self.visao_webcam.criar_elementos(canvas, pos_wx, pos_wy)
            self._timer_webcam_id = self.root.after(
                configuracao.TEMPO_ATIVAR_WEBCAM * 1000,
                self.ativar_stream_webcam
            )

        # Constrói o mapa mundi no canto inferior direito
        if configuracao.USAR_GEOLOCALIZACAO:
            if not self.estado.dados_geolocalizacao:
                self._preparar_mapa_global()
            mapa_x0 = tela_w - MAPA_LARGURA - 25
            mapa_y0 = tela_h - MAPA_ALTURA - 40
            self.visao_mapa.criar_elementos_mapa(
                canvas, mapa_x0, mapa_y0, self.estado.dados_geolocalizacao
            )
            self._iniciar_loop_mapa(canvas, mapa_x0, mapa_y0)

        # Inicia os laços de animações
        self._iniciar_loop_texto()
        self._iniciar_loop_barra()
        self._iniciar_loop_timer()
        self._iniciar_loop_popups()
        self._iniciar_loop_glitch()
        self._iniciar_loop_exclusao_arquivos()

    def desativar_modo_hacker(self):
        """Encerra a tela cheia hacker, para a webcam e fecha todos os popups."""
        if configuracao.USAR_WEBCAM:
            self.servico_webcam.encerrar()
            self.visao_webcam.destruir()

        # Cancela todos os loops de animação ativos do Tkinter
        loops = [
            self._loop_texto_id, self._loop_barra_id, self._loop_popups_id,
            self._loop_timer_id, self._loop_glitch_id, self._loop_webcam_id,
            self._loop_deletar_id, self._loop_mapa_id, self._timer_webcam_id
        ]
        for loop_id in loops:
            if loop_id is not None:
                try:
                    self.root.after_cancel(loop_id)
                except Exception:
                    pass

        self._loop_texto_id = None
        self._loop_barra_id = None
        self._loop_popups_id = None
        self._loop_timer_id = None
        self._loop_glitch_id = None
        self._loop_webcam_id = None
        self._loop_deletar_id = None
        self._loop_mapa_id = None
        self._timer_webcam_id = None

        self.visao_mapa.limpar_animacoes()
        self.visao_popups.fechar_todos_popups()
        self.visao_hacker.fechar_telas()

        self.estado.resetar_sessao_hacker()
        log("Modo Hacker encerrado e timer de ociosidade resetado.", "SISTEMA")

    def ativar_stream_webcam(self):
        """Conecta a webcam real e dá início à atualização dos quadros de vídeo na interface."""
        if not self.visao_hacker.esta_ativa():
            return

        log("🔴 WEBCAM CONECTADA! TRANSMISSÃO AO VIVO INICIADA", "ALERTA")
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        self.visao_webcam.definir_status_transmitindo()
        self.servico_webcam.iniciar()
        self._loop_atualizacao_webcam()

    def _loop_atualizacao_webcam(self):
        """Lê o próximo frame da câmera e o envia para a VisaoWebcam a cada ~33ms."""
        if not self.visao_hacker.esta_ativa() or not self.servico_webcam.esta_aberta():
            return

        frame_tk = self.servico_webcam.capturar_frame(largura=180, altura=130)
        if frame_tk:
            self.visao_webcam.atualizar_frame_video(frame_tk)

        self._loop_webcam_id = self.root.after(33, self._loop_atualizacao_webcam)

    def _iniciar_loop_mapa(self, canvas: tk.Canvas, x_offset: int, y_offset: int):
        """Gerencia o ciclo de renderização das trajetórias e radares do mapa."""
        def passo():
            if not self.visao_hacker.esta_ativa() or not canvas.winfo_exists():
                return
            self.visao_mapa.animar_passo(
                canvas, x_offset, y_offset, self.estado.dados_geolocalizacao
            )
            self._loop_mapa_id = self.root.after(33, passo)

        passo()

    def _iniciar_loop_texto(self):
        """Anima a digitação progressiva dos comandos hacker no terminal central."""
        if not self.visao_hacker.esta_ativa():
            return

        if self.estado.texto_atual_idx < len(COMANDOS_HACKER):
            cmd = COMANDOS_HACKER[self.estado.texto_atual_idx]
            log(f"Terminal: {cmd}", "HACKER")
            texto_visivel = "\n".join(COMANDOS_HACKER[:self.estado.texto_atual_idx + 1])
            self.visao_hacker.atualizar_terminal(texto_visivel)
            self.estado.texto_atual_idx += 1
            self._loop_texto_id = self.root.after(600, self._iniciar_loop_texto)

    def _iniciar_loop_barra(self):
        """Controla o avanço da porcentagem na barra de progresso."""
        if not self.visao_hacker.esta_ativa():
            return

        limite_maximo = 95 if self.estado.texto_atual_idx < len(COMANDOS_HACKER) else 100

        if self.estado.progresso_atual < limite_maximo:
            self.estado.progresso_atual += random.randint(3, 7)
            if self.estado.progresso_atual > limite_maximo:
                self.estado.progresso_atual = limite_maximo

            self.visao_hacker.atualizar_barra_progresso(self.estado.progresso_atual)
            self._loop_barra_id = self.root.after(300, self._iniciar_loop_barra)
        elif self.estado.progresso_atual >= 100:
            self._loop_piscar_tela_final()
        else:
            self._loop_barra_id = self.root.after(300, self._iniciar_loop_barra)

    def _loop_piscar_tela_final(self):
        """Alterna as cores de fundo ao atingir 100% de conclusão do ataque."""
        if not self.visao_hacker.esta_ativa():
            return

        self.estado.estado_piscar = not self.estado.estado_piscar
        self.visao_hacker.alternar_flash_final(self.estado.estado_piscar)
        cor = '#260000' if self.estado.estado_piscar else '#000000'
        self.visao_webcam.alterar_cor_fundo(cor)

        self._loop_barra_id = self.root.after(350, self._loop_piscar_tela_final)

    def _iniciar_loop_timer(self):
        """Atualiza a contagem regressiva em segundos até o bloqueio fictício."""
        if not self.visao_hacker.esta_ativa():
            return

        if self.estado.tempo_restante_contador > 0:
            m = self.estado.tempo_restante_contador // 60
            s = self.estado.tempo_restante_contador % 60
            self.visao_hacker.atualizar_timer(m, s)
            self.estado.tempo_restante_contador -= 1
            self._loop_timer_id = self.root.after(1000, self._iniciar_loop_timer)
        else:
            self.visao_hacker.definir_timer_esgotado()

    def _iniciar_loop_popups(self):
        """Dispara periodicamente novas janelas de erro críticas falsas."""
        if not self.visao_hacker.esta_ativa():
            return

        self.visao_popups.disparar_popup_falso(
            ao_clicar_ok=self.mostrar_revelacao
        )
        self._loop_popups_id = self.root.after(3500, self._iniciar_loop_popups)

    def _iniciar_loop_glitch(self):
        """Aplica glitches gráficos rápidos no texto central."""
        if not self.visao_hacker.esta_ativa():
            return

        self.visao_hacker.aplicar_glitch()
        self._loop_glitch_id = self.root.after(random.randint(400, 1200), self._iniciar_loop_glitch)

    def _iniciar_loop_exclusao_arquivos(self):
        """Simula a exclusão rápida de arquivos locais no Canvas."""
        if not self.visao_hacker.esta_ativa():
            return

        self.visao_hacker.simular_exclusao_arquivo()
        self._loop_deletar_id = self.root.after(350, self._iniciar_loop_exclusao_arquivos)

    def mostrar_revelacao(self):
        """Exibe a tela de revelação da pegadinha e encerra os demais alertas."""
        self.estado.registrar_atividade_usuario()
        self.visao_popups.exibir_revelacao_pegadinha(
            ao_fechar_tudo=self.desativar_modo_hacker
        )

    def ao_pressionar_esc(self):
        """Trata o cancelamento imediato ao pressionar a tecla ESC."""
        if self.visao_hacker.esta_ativa() or len(self.visao_popups.janelas_popups) > 0:
            log("Tecla ESC pressionada! Fechando tudo...", "CANCELAR")
            try:
                self.root.after(0, self.desativar_modo_hacker)
            except Exception:
                self.desativar_modo_hacker()
        self.estado.registrar_atividade_usuario()

    def ao_interagir_usuario(self):
        """Notifica o estado sobre qualquer atividade do usuário no sistema."""
        if not self.visao_hacker.esta_ativa():
            self.estado.registrar_atividade_usuario()

    def encerrar_aplicacao(self):
        """Encerra com segurança todos os serviços, listeners e a interface Tkinter."""
        log("Encerrando aplicação...", "SAIR")
        try:
            self.desativar_modo_hacker()
        except Exception:
            pass

        try:
            self.monitor_entrada.parar()
        except Exception:
            pass

        if configuracao.USAR_WEBCAM:
            try:
                self.servico_webcam.encerrar()
            except Exception:
                pass

        try:
            self.visao_bandeja.parar()
        except Exception:
            pass

        def _fechar_tk():
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass

        try:
            self.root.after(0, _fechar_tk)
        except Exception:
            _fechar_tk()
