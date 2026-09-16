import pyautogui
import time
import random

# Intervalo em segundos (60s = 1 minuto)
INTERVALO = 60

def mover_mouse():
    while True:
        x, y = pyautogui.position()

        # pequeno movimento aleatório (evita padrão fixo)
        novo_x = x + random.randint(-20, 20)
        novo_y = y + random.randint(-20, 20)

        pyautogui.moveTo(novo_x, novo_y, duration=0.5)

        # opcional: pequeno "click invisível"
        # pyautogui.click()

        time.sleep(INTERVALO)

if __name__ == "__main__":
    print("Rodando... CTRL+C para parar")
    mover_mouse()