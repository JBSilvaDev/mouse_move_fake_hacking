import os
import random
import socket
import threading
import time
import winsound
import json
import urllib.request
import io
import math
from datetime import datetime
import cv2
import pyautogui
import pystray
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from pynput import keyboard, mouse
from screeninfo import get_monitors

# ================= CONFIGURAÇÕES =================
TEMPO_OCIOSO_ALVO = 120     # Segundos sem mexer para ativar a pegadinha
INTERVALO_MOVER_MOUSE = 100  # Intervalo para mover o mouse (Anti-Teams)
MAX_POPUPS = 7              # Limite máximo de janelas de erro
TEMPO_CONTADOR_SEG = 180    # 3 minutos de contagem regressiva
USAR_WEBCAM = True          # True = Exibe webcam / False = Desativa webcam
TEMPO_ATIVAR_WEBCAM = 8     # Segundos após a invasão para ligar a webcam (Timer da câmera)
USAR_GEOLOCALIZACAO = True  # True = Busca localização e exibe o MAPA REAL
# ==================================================

NOME_USUARIO = os.getlogin().upper()
NOME_PC = socket.gethostname().upper()

ultimo_movimento = time.time()
ultimo_movimento_mouse = time.time()
movendo_pelo_script = False

janelas_hacker = []
janelas_popups = [] 
texto_atual_idx = 0
progresso_atual = 0
tempo_restante_contador = TEMPO_CONTADOR_SEG
estado_piscar = False
cap = None
dados_geo = None

loop_texto_id = None
loop_barra_id = None
loop_popups_id = None
loop_timer_id = None
loop_glitch_id = None
loop_webcam_id = None
loop_deletar_id = None
timer_webcam_id = None
tray_icon = None

ARQUIVOS_PARA_DELETAR = [
    f"C:\\Users\\{NOME_USUARIO}\\Desktop\\Relatorios_Financeiros_2026.xlsx",
    f"C:\\Users\\{NOME_USUARIO}\\Documents\\Fotos_Pessoais_Backup.zip",
    f"C:\\Users\\{NOME_USUARIO}\\Downloads\\Carteira_Crypto_Chaves.dat",
    f"C:\\Users\\{NOME_USUARIO}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
    f"C:\\Users\\{NOME_USUARIO}\\Documents\\Contratos_Assinados.pdf",
    f"C:\\Users\\{NOME_USUARIO}\\.ssh\\id_rsa",
    f"C:\\Windows\\System32\\drivers\\etc\\hosts"
]

COMANDOS_HACKER = [
    f"[!] ALVO IDENTIFICADO: HOST='{NOME_PC}' | USER='{NOME_USUARIO}'",
    "[+] INICIALIZANDO KERNEL EXPLOIT (CVE-2026-9981)...",
    "[+] TRIANGULANDO COORDENADAS GPS E IP PÚBLICO...",
    "[!] BYPASSING FIREWALL CORPORATIVO E VPN...",
    "[!] DESATIVANDO WINDOWS DEFENDER E AGENTE DE EDR...",
    "[+] ACESSO ROOT CONCEDIDO AO SUBSISTEMA.",
    "[>] STREAMING DE WEBCAM AGENDADO...",
    "[>] EXTRAINDO SENHAS SALVAS DO CHROME / EDGE...",
    "[>] SEQUESTRANDO TOKENS DE SESSÃO DO TEAMS E SLACK...",
    "[+] INSTALANDO KEYLOGGER EM NÍVEL DE DRIVER DE TECLADO...",
    "[>] COPIANDO DIRETÓRIO 'Documentos' PARA /root/exfiltrated_data/...",
    "[>] EXFILTRANDO CHAVES SSH E CERTIFICADOS DE REDE...",
    "[!] DELETANDO CÓPIAS DE SOMBRA (VSS) E BACKUPS LOCAIS...",
    "[!] ALERTA CRÍTICO: CHAVE DE CRIPTOGRAFIA DE DISCO ALTERADA.",
    "--- PRESSIONE ESC PARA INTERROMPER O PROCESSO ---"
]

pyautogui.FAILSAFE = False

def log(mensagem, categoria="INFO"):
    hora_atual = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora_atual}] [{categoria}] {mensagem}")

# --- GEOLOCALIZAÇÃO E MAPA REAL ---
def obter_geolocalizacao():
    try:
        url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return data
    except Exception:
        pass
    return {
        "query": "189.120.45.102",
        "city": "SÃO PAULO",
        "regionName": "SP",
        "country": "BRASIL",
        "lat": -23.5505,
        "lon": -46.6333,
        "isp": "TELEFONICA BRASIL"
    }

def obter_imagem_mapa_real(lat, lon, zoom=12):
    try:
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        
        url = f"https://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        with urllib.request.urlopen(req, timeout=4) as resp:
            img_data = resp.read()
            
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        img = img.resize((210, 120), Image.Resampling.LANCZOS)
        
        # Desenha mira de satélite em cima do mapa
        draw = ImageDraw.Draw(img)
        cx, cy = 105, 60
        draw.ellipse([cx-10, cy-10, cx+10, cy+10], outline="#ff0033", width=2)
        draw.line([cx-15, cy, cx+15, cy], fill="#ff0033", width=2)
        draw.line([cx, cy-15, cx, cy+15], fill="#ff0033", width=2)
        return img
    except Exception as e:
        log(f"Falha ao carregar mapa real: {e}", "ERRO")
        img = Image.new("RGB", (210, 120), color=(10, 20, 10))
        draw = ImageDraw.Draw(img)
        draw.text((30, 50), "[ MAPA OFFLINE ]", fill="#00ff41")
        return img

# --- MONITORAMENTO DE ENTRADAS ---
def ao_mexer_mouse(*args):
    global ultimo_movimento
    if movendo_pelo_script:
        return
    if not janelas_hacker:
        ultimo_movimento = time.time()

def ao_pressionar_tecla(key):
    global ultimo_movimento
    if janelas_hacker:
        if key == keyboard.Key.esc:
            log("Tecla ESC pressionada! Fechando tudo...", "CANCELAR")
            fechar_todas_as_telas()
            ultimo_movimento = time.time()
    else:
        ultimo_movimento = time.time()

listener_mouse = mouse.Listener(on_move=ao_mexer_mouse, on_click=ao_mexer_mouse, on_scroll=ao_mexer_mouse)
listener_teclado = keyboard.Listener(on_press=ao_pressionar_tecla)
listener_mouse.start()
listener_teclado.start()

# --- WEBCAM COM TIMER E STREAM ---
def agendar_webcam(lbl_video, lbl_rec_header):
    global timer_webcam_id
    if not janelas_hacker:
        return
    timer_webcam_id = root.after(TEMPO_ATIVAR_WEBCAM * 1000, lambda: ativar_stream_webcam(lbl_video, lbl_rec_header))

def ativar_stream_webcam(lbl_video, lbl_rec_header):
    global janelas_hacker
    if not janelas_hacker:
        return

    log("🔴 WEBCAM CONECTADA! TRANSMISSÃO AO VIVO INICIADA", "ALERTA")
    
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass

    if lbl_rec_header.winfo_exists():
        lbl_rec_header.config(text="🔴 LIVE STREAMING (TRANSMITINDO)", fg="#ff0033")

    # Inicia captura de vídeo real
    iniciar_webcam_real(lbl_video)

def iniciar_webcam_real(label_video):
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)

    def atualizar_frame():
        global cap, loop_webcam_id, janelas_hacker
        if not janelas_hacker or cap is None or not cap.isOpened():
            return

        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (180, 130))
            img_pil = Image.fromarray(frame_resized)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            
            label_video.img_tk = img_tk
            label_video.config(image=img_tk)

        loop_webcam_id = root.after(33, atualizar_frame)

    atualizar_frame()

def fechar_webcam_real():
    global cap
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None

def fechar_todas_as_telas():
    global janelas_hacker, janelas_popups, loop_texto_id, loop_barra_id, loop_popups_id
    global loop_timer_id, loop_glitch_id, loop_webcam_id, loop_deletar_id, timer_webcam_id

    if USAR_WEBCAM:
        fechar_webcam_real()

    for id_loop in [loop_texto_id, loop_barra_id, loop_popups_id, loop_timer_id, loop_glitch_id, loop_webcam_id, loop_deletar_id, timer_webcam_id]:
        if id_loop:
            try:
                root.after_cancel(id_loop)
            except Exception:
                pass

    loop_texto_id = loop_barra_id = loop_popups_id = loop_timer_id = loop_glitch_id = loop_webcam_id = loop_deletar_id = timer_webcam_id = None

    for jp in janelas_popups:
        try:
            jp.destroy()
        except Exception:
            pass
    janelas_popups.clear()

    for j in janelas_hacker:
        try:
            j.destroy()
        except Exception:
            pass
    janelas_hacker.clear()
    log("Modo Hacker encerrado.", "SISTEMA")

def verificar_sistema():
    global ultimo_movimento, ultimo_movimento_mouse, janelas_hacker, movendo_pelo_script
    tempo_atual = time.time()
    tempo_inativo = tempo_atual - ultimo_movimento

    if tempo_inativo >= TEMPO_OCIOSO_ALVO and not janelas_hacker:
        log(f"Inatividade de {int(tempo_inativo)}s. Ativando Tela Hacker...", "ALERTA")
        criar_janelas_hacker()

    if tempo_atual - ultimo_movimento_mouse >= INTERVALO_MOVER_MOUSE:
        x, y = pyautogui.position()
        novo_x = x + random.randint(-15, 15)
        novo_y = y + random.randint(-15, 15)
        
        movendo_pelo_script = True
        pyautogui.moveTo(novo_x, novo_y, duration=0.3)
        movendo_pelo_script = False
        
        ultimo_movimento_mouse = tempo_atual
        log(f"Mouse ajustado preventivamente para ({novo_x}, {novo_y})", "MONITOR")

    root.after(500, verificar_sistema)

# --- INTERFACE PRINCIPAL ---
def criar_janelas_hacker():
    global janelas_hacker, texto_atual_idx, progresso_atual, tempo_restante_contador, dados_geo
    texto_atual_idx = 0
    progresso_atual = 0
    tempo_restante_contador = TEMPO_CONTADOR_SEG
    janelas_hacker.clear()

    if USAR_GEOLOCALIZACAO and dados_geo is None:
        dados_geo = obter_geolocalizacao()

    try:
        winsound.MessageBeep(winsound.MB_ICONHAND)
    except Exception:
        pass

    monitores = get_monitors()
    for m in monitores:
        j = tk.Toplevel(root)
        j.withdraw()
        j.geometry(f"{m.width}x{m.height}+{m.x}+{m.y}")
        j.overrideredirect(True)
        j.attributes('-topmost', True)
        j.configure(bg='black')
        j.config(cursor="none")
        j.deiconify()
        janelas_hacker.append(j)

    janela_principal = janelas_hacker[0]

    # --- WEBCAM COM TIMER (CANTO SUPERIOR ESQUERDO) ---
    if USAR_WEBCAM:
        frame_webcam = tk.Frame(janela_principal, bg='black', highlightbackground='#ff0033', highlightthickness=2)
        frame_webcam.place(relx=0.03, rely=0.03, anchor="nw")

        lbl_rec_header = tk.Label(
            frame_webcam, text=f"⏳ WEBCAM (INICIANDO EM {TEMPO_ATIVAR_WEBCAM}s...)", fg="#ffcc00", bg="black", font=("Consolas", 7, "bold")
        )
        lbl_rec_header.pack(anchor="w", padx=3, pady=(2, 0))

        lbl_video = tk.Label(
            frame_webcam, 
            text="\n  [ CONECTANDO SERVIDOR DE STREAMING ]  \n  [ AGUARDANDO LIBERAÇÃO DA CÂMERA ]  \n", 
            fg="#ff5555", bg="black", font=("Consolas", 8)
        )
        lbl_video.pack(padx=3, pady=3)

        agendar_webcam(lbl_video, lbl_rec_header)

    # --- GEOLOCALIZAÇÃO & MAPA REAL (CANTO INFERIOR ESQUERDO) ---
    if USAR_GEOLOCALIZACAO and dados_geo:
        frame_geo = tk.Frame(janela_principal, bg='black', highlightbackground='#00ff41', highlightthickness=1)
        frame_geo.place(relx=0.03, rely=0.97, anchor="sw")

        tk.Label(frame_geo, text="🎯 RASTREAMENTO GPS DA VÍTIMA", fg="#00ff41", bg="black", font=("Consolas", 8, "bold")).pack(anchor="w", padx=5, pady=(3, 2))

        # Renderiza imagem do mapa real em tempo de execução
        img_mapa_pil = obter_imagem_mapa_real(dados_geo.get('lat', -23.55), dados_geo.get('lon', -46.63))
        img_mapa_tk = ImageTk.PhotoImage(img_mapa_pil)
        
        lbl_mapa = tk.Label(frame_geo, image=img_mapa_tk, bg="black")
        lbl_mapa.img_tk = img_mapa_tk
        lbl_mapa.pack(padx=5, pady=2)

        info_text = (
            f"IP: {dados_geo.get('query')}\n"
            f"LOCAL: {str(dados_geo.get('city')).upper()} - {dados_geo.get('regionName')}\n"
            f"COORD: {dados_geo.get('lat')}, {dados_geo.get('lon')}\n"
            f"ISP: {str(dados_geo.get('isp')).upper()[:22]}"
        )
        tk.Label(frame_geo, text=info_text, fg="#00ff41", bg="black", font=("Consolas", 7), justify="left").pack(anchor="w", padx=5, pady=(0, 4))

    # --- PAINEL CENTRAL ---
    global frame_centro
    frame_centro = tk.Frame(janela_principal, bg='black')
    frame_centro.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    global frame_titulo, lbl_titulo
    frame_titulo = tk.Frame(frame_centro, bg="black")
    frame_titulo.pack(pady=(0, 5))

    tk.Label(frame_titulo, text="⚠️ ", fg="#ffcc00", bg="black", font=("Consolas", 20, "bold")).pack(side=tk.LEFT)
    lbl_titulo = tk.Label(frame_titulo, text="FALHA DE SEGURANÇA: SISTEMA COMPROMETIDO", fg="#ff0033", bg="black", font=("Consolas", 20, "bold"))
    lbl_titulo.pack(side=tk.LEFT)
    tk.Label(frame_titulo, text=" ⚠️", fg="#ffcc00", bg="black", font=("Consolas", 20, "bold")).pack(side=tk.LEFT)

    lbl_sub = tk.Label(frame_centro, text="[STATUS: INVASÃO REMOTA EM ANDAMENTO - NÃO DESLIGUE O PC]", fg="#ff5555", bg="black", font=("Consolas", 11, "bold"))
    lbl_sub.pack(pady=(0, 8))

    global lbl_timer
    lbl_timer = tk.Label(frame_centro, text="TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: 03:00", fg="#ff0033", bg="black", font=("Consolas", 12, "bold"))
    lbl_timer.pack(pady=(0, 8))

    global lbl_terminal
    lbl_terminal = tk.Label(frame_centro, text="", fg="#00ff41", bg="black", font=("Consolas", 10), justify="left")
    lbl_terminal.pack(pady=(0, 8))

    global lbl_deletando
    lbl_deletando = tk.Label(frame_centro, text="[AGUARDANDO VARREDURA DE DISCO...]", fg="#ffcc00", bg="black", font=("Consolas", 9, "italic"))
    lbl_deletando.pack(pady=(0, 8))

    global lbl_barra
    lbl_barra = tk.Label(frame_centro, text="[░░░░░░░░░░░░░░░░░░░░] 0%", fg="#00ff41", bg="black", font=("Consolas", 13, "bold"))
    lbl_barra.pack()

    animar_texto()
    animar_barra()
    atualizar_timer()
    disparar_popups_falsos()
    aplicar_glitch()
    animar_exclusao_arquivos()

# --- ANIMAÇÕES E EFEITOS ---
def aplicar_glitch():
    global loop_glitch_id, janelas_hacker
    if not janelas_hacker:
        return

    if random.random() < 0.4:
        off_x = random.choice([-8, -4, -2, 2, 4, 8])
        off_y = random.choice([-8, -4, -2, 2, 4, 8])
        frame_centro.place(relx=0.5, rely=0.5, x=off_x, y=off_y, anchor=tk.CENTER)
        
        if random.random() < 0.25:
            frame_centro.configure(bg='#330000')
            
        root.after(60, restaurar_posicao_glitch)

    loop_glitch_id = root.after(random.randint(400, 1200), aplicar_glitch)

def restaurar_posicao_glitch():
    if janelas_hacker and frame_centro.winfo_exists():
        frame_centro.place(relx=0.5, rely=0.5, x=0, y=0, anchor=tk.CENTER)
        frame_centro.configure(bg='black')

def animar_exclusao_arquivos():
    global loop_deletar_id, janelas_hacker
    if not janelas_hacker:
        return

    arquivo = random.choice(ARQUIVOS_PARA_DELETAR)
    if 'lbl_deletando' in globals() and lbl_deletando.winfo_exists():
        lbl_deletando.config(text=f"[DELETANDO ARQUIVO] {arquivo} ... [APAGADO]")

    loop_deletar_id = root.after(350, animar_exclusao_arquivos)

def atualizar_timer():
    global tempo_restante_contador, loop_timer_id, janelas_hacker
    if not janelas_hacker:
        return

    if tempo_restante_contador > 0:
        minutos = tempo_restante_contador // 60
        segundos = tempo_restante_contador % 60
        lbl_timer.config(text=f"TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: {minutos:02d}:{segundos:02d}")
        tempo_restante_contador -= 1
        loop_timer_id = root.after(1000, atualizar_timer)
    else:
        lbl_timer.config(text="TEMPO ESGOTADO - SISTEMA CRIPTOGRAFADO!")

def animar_texto():
    global texto_atual_idx, loop_texto_id, janelas_hacker
    if not janelas_hacker:
        return

    if texto_atual_idx < len(COMANDOS_HACKER):
        cmd = COMANDOS_HACKER[texto_atual_idx]
        log(f"Terminal: {cmd}", "HACKER")
        texto_atual = "\n".join(COMANDOS_HACKER[:texto_atual_idx + 1])
        lbl_terminal.config(text=texto_atual)
        texto_atual_idx += 1
        loop_texto_id = root.after(600, animar_texto)

def animar_barra():
    global progresso_atual, loop_barra_id, janelas_hacker
    if not janelas_hacker:
        return

    limite_maximo = 95 if texto_atual_idx < len(COMANDOS_HACKER) else 100

    if progresso_atual < limite_maximo:
        progresso_atual += random.randint(3, 7)
        if progresso_atual > limite_maximo: 
            progresso_atual = limite_maximo
            
        blocos = int(progresso_atual / 5)
        barra_str = "[" + "█" * blocos + "░" * (20 - blocos) + f"] {progresso_atual}%"
        lbl_barra.config(text=barra_str)
        loop_barra_id = root.after(300, animar_barra)
    elif progresso_atual >= 100:
        piscar_tela_final()
    else:
        loop_barra_id = root.after(300, animar_barra)

# --- REVELAÇÃO DA PEGADINHA ---
def mostrar_revelacao_pegadinha():
    for jp in janelas_popups:
        try:
            jp.destroy()
        except Exception:
            pass
    janelas_popups.clear()

    try:
        popup_rev = tk.Toplevel(root)
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
            command=fechar_todas_as_telas
        )
        btn_fechar.pack(pady=(15, 0))

        popup_rev.deiconify()
        popup_rev.lift()
        janelas_popups.append(popup_rev)

        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception as e:
        log(f"Erro ao exibir revelação: {e}", "ERRO")

def disparar_popups_falsos():
    global loop_popups_id, janelas_hacker, janelas_popups
    if not janelas_hacker:
        return

    mensagens_erro = [
        ("Erro crítico de Kernel", f"Falha de proteção em 0x00007FF7 no processo '{NOME_PC}'."),
        ("Aviso de Segurança", "Acesso não autorizado à webcam e microfone confirmado."),
        ("Windows Defender", f"Múltiplos arquivos de '{NOME_USUARIO}' enviados para servidor externo."),
        ("Atenção Alerta", "Sua chave de recuperação BitLocker foi alterada remotamente.")
    ]
    
    titulo, texto = random.choice(mensagens_erro)
    
    try:
        popup = tk.Toplevel(root)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        
        monitor = get_monitors()[0]
        zona = random.choice(["top", "bottom", "left", "right"])
        
        if zona == "top":
            px = random.randint(monitor.x + 50, monitor.x + monitor.width - 450)
            py = random.randint(monitor.y + 30, monitor.y + int(monitor.height * 0.15))
        elif zona == "bottom":
            px = random.randint(monitor.x + 50, monitor.x + monitor.width - 450)
            py = random.randint(monitor.y + int(monitor.height * 0.82), monitor.y + monitor.height - 180)
        elif zona == "left":
            px = random.randint(monitor.x + 30, monitor.x + int(monitor.width * 0.15))
            py = random.randint(monitor.y + 50, monitor.y + monitor.height - 180)
        else:
            px = random.randint(monitor.x + int(monitor.width * 0.82), monitor.x + monitor.width - 450)
            py = random.randint(monitor.y + 50, monitor.y + monitor.height - 180)

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

        lbl_txt_pop = tk.Label(conteudo, text=texto, fg="#00ff41", bg="black", font=("Consolas", 8), wraplength=370, justify="left")
        lbl_txt_pop.pack(anchor="w", padx=10, pady=(0, 10))

        btn_ok = tk.Button(
            conteudo, text="OK", bg="#ff0033", fg="white",
            activebackground="#cc0028", activeforeground="white",
            font=("Consolas", 8, "bold"), relief="flat", highlightthickness=0, bd=0,
            command=mostrar_revelacao_pegadinha
        )
        btn_ok.pack(pady=(0, 8))

        popup.deiconify()
        popup.lift()

        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass

        janelas_popups.append(popup)

        while len(janelas_popups) > MAX_POPUPS:
            p_antigo = janelas_popups.pop(0)
            try:
                p_antigo.destroy()
            except Exception:
                pass
    except Exception:
        pass

    loop_popups_id = root.after(3500, disparar_popups_falsos)

def piscar_tela_final():
    global loop_barra_id, janelas_hacker, estado_piscar
    if not janelas_hacker:
        return

    estado_piscar = not estado_piscar
    
    for idx, j in enumerate(janelas_hacker):
        if estado_piscar:
            j.configure(bg='#260000')
            if idx == 0:
                frame_centro.configure(bg='#260000')
                frame_titulo.configure(bg='#260000')
                lbl_titulo.configure(bg='#260000', fg='white')
                lbl_timer.configure(bg='#260000', fg='yellow')
                lbl_terminal.configure(bg='#260000', fg='#ff0033')
                lbl_barra.configure(bg='#260000', fg='#ff0033', text="[████████████████████] DADOS ROUBADOS [100%]")
        else:
            j.configure(bg='black')
            if idx == 0:
                frame_centro.configure(bg='black')
                frame_titulo.configure(bg="black")
                lbl_titulo.configure(bg='black', fg='#ff0033')
                lbl_timer.configure(bg='black', fg='#ff0033')
                lbl_terminal.configure(bg='black', fg='#00ff41')
                lbl_barra.configure(bg='black', fg='#00ff41', text="[████████████████████] SISTEMA BLOQUEADO [100%]")

    loop_barra_id = root.after(350, piscar_tela_final)

def sair_programa(icon, item):
    log("Encerrando aplicação...", "SAIR")
    listener_mouse.stop()
    listener_teclado.stop()
    if USAR_WEBCAM:
        fechar_webcam_real()
    icon.stop()
    root.quit()

def setup_tray():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], outline='#00ff41', width=3)
    draw.text((24, 22), ">", fill='#ff0033')

    menu = pystray.Menu(
        pystray.MenuItem("Status: Protegido / Oculto", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair / Fechar", sair_programa)
    )
    
    global tray_icon
    tray_icon = pystray.Icon("AntiAusente", image, "Anti-Ausente Hacker", menu)
    tray_icon.run()

root = tk.Tk()
root.withdraw()

if __name__ == "__main__":
    print("==========================================================")
    print("   ANTI-AUSENTE HACKER - WEBCAM TIMER & MAPA REAL GPS     ")
    print("==========================================================")
    log("Iniciando monitoramento de ociosidade...", "INÍCIO")
    log(f"Host: {NOME_PC} | Usuário: {NOME_USUARIO}", "SISTEMA")

    root.after(500, verificar_sistema)

    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        log("Encerrando via teclado...", "SAIR")
        listener_mouse.stop()
        listener_teclado.stop()
        if USAR_WEBCAM:
            fechar_webcam_real()
        if tray_icon:
            tray_icon.stop()