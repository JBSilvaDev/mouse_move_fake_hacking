import pyautogui
import time
import random
import threading
import pystray
from PIL import Image, ImageDraw

INTERVALO = 60  # Defina o tempo desejado em segundos (ex: 60 = 1 min)
rodando = True

pyautogui.FAILSAFE = False

def mover_mouse():
    global rodando
    while rodando:
        time.sleep(INTERVALO)
        if not rodando:
            break
        try:
            dx = random.choice([-20, -10, 10, 20])
            dy = random.choice([-20, -10, 10, 20])
            pyautogui.moveRel(dx, dy, duration=0.2)
        except Exception:
            pass

def fechar_programa(icon, item):
    global rodando
    rodando = False
    icon.stop()

def criar_icone():
    # Cria a imagem do ícone (quadrado escuro com ponto verde)
    image = Image.new('RGB', (64, 64), color='#1e1e1e')
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill='#00ff41')

    menu = pystray.Menu(
        pystray.MenuItem("Status: Anti-Ausente Ativo", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair / Fechar", fechar_programa)
    )

    icon = pystray.Icon("AntiAusente", image, "Anti-Ausente Simples", menu)

    # Thread para a movimentação em segundo plano
    t = threading.Thread(target=mover_mouse, daemon=True)
    t.start()

    icon.run()

if __name__ == "__main__":
    criar_icone()