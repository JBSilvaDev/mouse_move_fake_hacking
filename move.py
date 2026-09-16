import time
import random
import pyautogui
from pynput import mouse, keyboard

# Configurações de tempo (em segundos)
TEMPO_OCIOSO_ALVO = 5      # 1 minuto sem mexer para ativar
INTERVALO_VERIFICACAO = 10  # De quanto em quanto tempo o script checa o PC

ultimo_movimento = time.time()

# Funções que resetam o cronômetro de ociosidade
def atualizar_tempo(*args):
    global ultimo_movimento
    ultimo_movimento = time.time()

# Inicia os ouvintes globais em segundo plano separando os eventos corretamente
listener_mouse = mouse.Listener(
    on_move=atualizar_tempo,
    on_click=lambda x, y, button, pressed: atualizar_tempo(),
    on_scroll=lambda x, y, dx, dy: atualizar_tempo()
)
listener_teclado = keyboard.Listener(
    on_press=atualizar_tempo,
    on_release=atualizar_tempo
)

listener_mouse.start()
listener_teclado.start()

if __name__ == "__main__":
    print("Monitor de ociosidade rodando... CTRL+C para parar")
    try:
        while True:
            time.sleep(INTERVALO_VERIFICACAO)
            
            # Calcula há quantos segundos o usuário está inativo
            tempo_inativo = time.time() - ultimo_movimento
            
            if tempo_inativo >= TEMPO_OCIOSO_ALVO:
                x, y = pyautogui.position()
                novo_x = x + random.randint(-20, 20)
                novo_y = y + random.randint(-20, 20)
                pyautogui.moveTo(novo_x, novo_y, duration=0.5)
                
                # Atualiza o tempo para o mouse não ficar tremendo sem parar
                ultimo_movimento = time.time()
                print(f"Movimento anti-ociosidade acionado após {int(tempo_inativo)}s parado.")
                
    except KeyboardInterrupt:
        print("\nEncerrando...")
        listener_mouse.stop()
        listener_teclado.stop()