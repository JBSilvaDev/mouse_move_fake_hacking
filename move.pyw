import time
import random
import threading
import pyautogui
import tkinter as tk
from pynput import mouse, keyboard
from screeninfo import get_monitors
import pystray
from PIL import Image, ImageDraw

# ================= CONFIGURAÇÕES =================
TEMPO_OCIOSO_ALVO = 100      # 1 minuto sem mexer para ativar a pegadinha
INTERVALO_MOVER_MOUSE = 90  # Intervalo para mover o mouse (Anti-Teams)
# ==================================================

ultimo_movimento = time.time()
ultimo_movimento_mouse = time.time()
movendo_pelo_script = False

janelas_hacker = []
janelas_popups = [] 
texto_atual_idx = 0
loop_texto_id = None
progresso_atual = 0
loop_barra_id = None
loop_popups_id = None
estado_piscar = False
tray_icon = None

COMANDOS_HACKER = [
    "[+] INICIALIZANDO KERNEL EXPLOIT (CVE-2026-9981)...",
    "[+] CONECTANDO AO SERVIDOR REMOTO (IP: 185.220.101.5:666)...",
    "[!] BYPASSING FIREWALL CORPORATIVO E VPN...",
    "[!] DESATIVANDO WINDOWS DEFENDER E AGENTE DE EDR...",
    "[+] ACESSO ROOT CONCEDIDO AO SUBSISTEMA.",
    "[>] CAPTURANDO WEBCAM E MICROFONE...",
    "[>] EXTRAINDO SENHAS SALVAS DO CHROME / EDGE...",
    "[>] SEQUESTRANDO TOKENS DE SESSÃO DO TEAMS E SLACK...",
    "[+] INSTALANDO KEYLOGGER EM NÍVEL DE DRIVER DE TECLADO...",
    "[>] COPIANDO DIRETÓRIO 'Documentos' PARA /root/exfiltrated_data/...",
    "[>] EXFILTRANDO CHAVES SSH E CERTIFICADOS DE REDE...",
    "[!] DELETANDO CÓPIAS DE SOMBRA (VSS) E BACKUPS LOCAIS...",
    "[!] ALERTA CRÍTICO: CHAVE DE CRIPTOGRAFIA DE DISCO ALTERADA.",
    "--- PRESSIONE ESC PARA INTERROMPER O PROCESSO ---"
]

def ao_mexer_mouse(*args):
    """Reseta a ociosidade apenas se for um movimento humano real"""
    global ultimo_movimento
    if movendo_pelo_script:
        return
    if not janelas_hacker:
        ultimo_movimento = time.time()

def ao_pressionar_tecla(key):
    """Detecta teclas: se a tela hacker estiver ativa, SOMENTE o ESC fecha tudo"""
    global ultimo_movimento
    if janelas_hacker:
        if key == keyboard.Key.esc:
            fechar_todas_as_telas()
            ultimo_movimento = time.time()
    else:
        ultimo_movimento = time.time()

listener_mouse = mouse.Listener(
    on_move=ao_mexer_mouse,
    on_click=ao_mexer_mouse,
    on_scroll=ao_mexer_mouse
)
listener_teclado = keyboard.Listener(
    on_press=ao_pressionar_tecla
)
listener_mouse.start()
listener_teclado.start()

def fechar_todas_as_telas():
    global janelas_hacker, janelas_popups, loop_texto_id, loop_barra_id, loop_popups_id
    if loop_texto_id:
        root.after_cancel(loop_texto_id)
        loop_texto_id = None
    if loop_barra_id:
        root.after_cancel(loop_barra_id)
        loop_barra_id = None
    if loop_popups_id:
        root.after_cancel(loop_popups_id)
        loop_popups_id = None

    for jp in janelas_popups:
        try:
            jp.destroy()
        except:
            pass
    janelas_popups.clear()

    for j in janelas_hacker:
        try:
            j.destroy()
        except:
            pass
    janelas_hacker.clear()

def verificar_sistema():
    global ultimo_movimento, ultimo_movimento_mouse, janelas_hacker, movendo_pelo_script
    tempo_atual = time.time()
    tempo_inativo = tempo_atual - ultimo_movimento

    if tempo_inativo >= TEMPO_OCIOSO_ALVO and not janelas_hacker:
        criar_janelas_hacker()

    if tempo_atual - ultimo_movimento_mouse >= INTERVALO_MOVER_MOUSE:
        x, y = pyautogui.position()
        novo_x = x + random.randint(-15, 15)
        novo_y = y + random.randint(-15, 15)
        
        movendo_pelo_script = True
        pyautogui.moveTo(novo_x, novo_y, duration=0.3)
        movendo_pelo_script = False
        
        ultimo_movimento_mouse = tempo_atual

    root.after(500, verificar_sistema)

def criar_janelas_hacker():
    global janelas_hacker, texto_atual_idx, progresso_atual
    texto_atual_idx = 0
    progresso_atual = 0
    janelas_hacker.clear()

    for m in get_monitors():
        j = tk.Toplevel(root)
        geometria = f"{m.width}x{m.height}+{m.x}+{m.y}"
        j.geometry(geometria)
        j.overrideredirect(True)
        j.attributes('-topmost', True)
        j.configure(bg='black')
        j.config(cursor="none")
        janelas_hacker.append(j)

    janela_principal = janelas_hacker[0]

    global frame_centro
    frame_centro = tk.Frame(janela_principal, bg='black')
    frame_centro.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    global frame_titulo
    frame_titulo = tk.Frame(frame_centro, bg="black")
    frame_titulo.pack(pady=(0, 15))

    tk.Label(frame_titulo, text="⚠️ ", fg="#ffcc00", bg="black", font=("Consolas", 24, "bold")).pack(side=tk.LEFT)
    
    global lbl_titulo
    lbl_titulo = tk.Label(
        frame_titulo, 
        text="FALHA DE SEGURANÇA: SISTEMA COMPROMETIDO", 
        fg="#ff0033", 
        bg="black", 
        font=("Consolas", 24, "bold")
    )
    lbl_titulo.pack(side=tk.LEFT)

    tk.Label(frame_titulo, text=" ⚠️", fg="#ffcc00", bg="black", font=("Consolas", 24, "bold")).pack(side=tk.LEFT)

    lbl_sub = tk.Label(
        frame_centro,
        text="[STATUS: INVASÃO REMOTA EM ANDAMENTO - NÃO DESLIGUE O PC]",
        fg="#ff5555",
        bg="black",
        font=("Consolas", 13, "bold")
    )
    lbl_sub.pack(pady=(0, 20))

    global lbl_terminal
    lbl_terminal = tk.Label(
        frame_centro, 
        text="", 
        fg="#00ff41", 
        bg="black", 
        font=("Consolas", 13),
        justify="left"
    )
    lbl_terminal.pack(pady=(0, 20))

    global lbl_barra
    lbl_barra = tk.Label(
        frame_centro,
        text="[░░░░░░░░░░░░░░░░░░░░] 0%",
        fg="#00ff41",
        bg="black",
        font=("Consolas", 15, "bold")
    )
    lbl_barra.pack()

    animar_texto()
    animar_barra()
    disparar_popups_falsos()

def animar_texto():
    global texto_atual_idx, loop_texto_id, janelas_hacker
    if not janelas_hacker:
        return

    if texto_atual_idx < len(COMANDOS_HACKER):
        texto_atual = "\n".join(COMANDOS_HACKER[:texto_atual_idx + 1])
        lbl_terminal.config(text=texto_atual)
        texto_atual_idx += 1
        loop_texto_id = root.after(700, animar_texto)

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

def disparar_popups_falsos():
    global loop_popups_id, janelas_hacker, janelas_popups
    if not janelas_hacker:
        return

    mensagens_erro = [
        ("Erro crítico de Kernel", "Falha de proteção de memória em 0x00007FF7. Despejo de memória iniciado."),
        ("Aviso de Segurança", "Tentativa de acesso não autorizado à webcam bloqueada parcialmente."),
        ("Windows Defender", "Múltiplos arquivos compactados e enviados para IP externo."),
        ("Atenção", "Seu IP foi registrado e reportado ao administrador de rede.")
    ]
    
    titulo, texto = random.choice(mensagens_erro)
    
    try:
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        
        monitor_primario = get_monitors()[0]
        px = random.randint(monitor_primario.x + 100, monitor_primario.x + monitor_primario.width - 500)
        py = random.randint(monitor_primario.y + 100, monitor_primario.y + monitor_primario.height - 300)
        popup.geometry(f"400x150+{px}+{py}")
        popup.configure(bg='#111111')

        moldura = tk.Frame(popup, bg='#ff0033', bd=2)
        moldura.pack(fill=tk.BOTH, expand=True)

        conteudo = tk.Frame(moldura, bg='black')
        conteudo.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        frame_tit_pop = tk.Frame(conteudo, bg="black")
        frame_tit_pop.pack(anchor="w", padx=10, pady=(10, 5))

        tk.Label(frame_tit_pop, text="⚠️ ", fg="#ffcc00", bg="black", font=("Consolas", 11, "bold")).pack(side=tk.LEFT)
        tk.Label(frame_tit_pop, text=titulo.upper(), fg="#ff0033", bg="black", font=("Consolas", 11, "bold")).pack(side=tk.LEFT)

        lbl_txt_pop = tk.Label(conteudo, text=texto, fg="#00ff41", bg="black", font=("Consolas", 10), wraplength=370, justify="left")
        lbl_txt_pop.pack(anchor="w", padx=10, pady=(0, 15))

        btn_ok = tk.Button(conteudo, text="OK", bg="#ff0033", fg="white", font=("Consolas", 9, "bold"), relief="flat", command=popup.destroy)
        btn_ok.pack(pady=(0, 10))

        janelas_popups.append(popup)
    except:
        pass

    loop_popups_id = root.after(4000, disparar_popups_falsos)

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
                lbl_terminal.configure(bg='#260000', fg='#ff0033')
                lbl_barra.configure(bg='#260000', fg='#ff0033', text="[████████████████████] DADOS ROUBADOS [100%]")
        else:
            j.configure(bg='black')
            if idx == 0:
                frame_centro.configure(bg='black')
                frame_titulo.configure(bg="black")
                lbl_titulo.configure(bg='black', fg='#ff0033')
                lbl_terminal.configure(bg='black', fg='#00ff41')
                lbl_barra.configure(bg='black', fg='#00ff41', text="[████████████████████] SISTEMA BLOQUEADO [100%]")

    loop_barra_id = root.after(350, piscar_tela_final)

def sair_programa(icon, item):
    listener_mouse.stop()
    listener_teclado.stop()
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
root.after(500, verificar_sistema)

tray_thread = threading.Thread(target=setup_tray, daemon=True)
tray_thread.start()

if __name__ == "__main__":
    try:
        root.mainloop()
    except KeyboardInterrupt:
        listener_mouse.stop()
        listener_teclado.stop()
        if tray_icon:
            tray_icon.stop()