# Anti-Ausente Hacker (Mouse Move) 🖱️

Utilitário em Python que previne o status "Ausente" em aplicativos de comunicação (como Teams, Slack e Discord) e inclui um "Modo Susto/Hacker" ativado por ociosidade.

## 📌 Sobre o Projeto

O programa roda de forma invisível em segundo plano (background) e executa as seguintes funções:

1. **Anti-Ausente Inteligente:** Move ligeiramente o cursor a cada 45 segundos para manter a sessão ativa. O script diferencia movimentos automatizados de interações humanas, garantindo que o Teams continue "Disponível" sem interferir na contagem do tempo de ociosidade.
2. **Modo Hacker (Protetor de Tela):** Se o computador ficar inativo por 60 segundos (sem toque humano no mouse ou teclado), o script cobre todos os monitores com uma tela simulando uma invasão, exibindo comandos em tempo real, barra de progresso sincronizada e pop-ups de erro crítico.
3. **Desativação Exclusiva via ESC:** Durante a exibição da tela hacker, movimentações de mouse e outras teclas são ignoradas. Somente ao pressionar a tecla **`ESC`** a tela é encerrada e o sistema retorna ao normal.
4. **Bandeja do Sistema (System Tray):** Um ícone discreto fica ativo ao lado do relógio do Windows para encerramento rápido com o botão direito.

---

## ⚙️ Requisitos

- **Python 3.8+**
- Sistema operacional **Windows** (recomendado para suporte a `.pyw` e `.bat`)
- Dependências listadas abaixo (`pyautogui`, `pynput`, `screeninfo`, `pystray`, `pillow`)

---

## 🚀 Instalação

1. Abra o terminal na pasta do projeto, crie e ative o ambiente virtual:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

```

2. Instale as dependências necessárias:
```powershell
pip install pyautogui pynput screeninfo pystray pillow

```



---

## 🛠️ Arquivos do Projeto (`.pyw` e `.bat`)

### 1. O arquivo `.pyw` (`move.pyw`)

A extensão `.pyw` avisa o Windows para executar o script através do `pythonw.exe`, garantindo que nenhuma janela preta de terminal (CMD) fique visível durante a execução.

### 2. O arquivo de inicialização `play.bat`

Para iniciar o script com um duplo clique sem abrir o terminal nem precisar ativar o `venv` manualmente, crie um arquivo chamado `play.bat` na raiz do projeto:

```bat
@echo off
start "" "venv\Scripts\pythonw.exe" "move.pyw"
exit

```

---

## 💻 Como Usar

### Iniciando o programa

Dê um **duplo clique no arquivo `executar.bat**`. O programa iniciará silenciosamente em segundo plano e exibirá um ícone na **Bandeja do Sistema (System Tray)**, ao lado do relógio do Windows.

### Encerrando o programa

1. Vá até a **Bandeja do Sistema** (ao lado do relógio).
2. Clique com o **botão direito** no ícone do aplicativo.
3. Selecione a opção **"Sair / Fechar"**.

---

## 🔧 Configurações

Os intervalos de tempo e ociosidade podem ser ajustados no topo do arquivo `move.pyw`:

```python
# ================= CONFIGURAÇÕES =================
TEMPO_OCIOSO_ALVO = 60      # Tempo sem interação humana (em segundos) para ativar a tela hacker
INTERVALO_MOVER_MOUSE = 45  # Intervalo (em segundos) para movimentação automática (Anti-Teams)
# ==================================================

```

---

## 🧠 Estrutura e Bibliotecas

* **`pyautogui`**: Realiza micro-movimentos no mouse para manter a sessão do sistema e dos apps ativa.
* **`pynput`**: Monitora eventos globais de entrada, permitindo capturar a tecla `ESC` e diferenciar interações humanas do movimento do robô.
* **`screeninfo`**: Mapeia a resolução de múltiplos monitores para cobrir todas as telas ao ativar o modo hacker.
* **`pystray` + `Pillow**`: Gerencia o ícone e o menu de encerramento na bandeja do sistema.

---

## ⚠️ Observações Importantes

* **Sair da Tela Hacker:** Lembre-se de pressionar a tecla **`ESC`** para fechar a tela de ociosidade e liberar a área de trabalho.
* **Início Automático com o Windows:** Para inicializar o script junto com o Windows, pressione `Win + R`, digite `shell:startup` e cole um atalho do arquivo `play.bat` dentro da pasta que se abrir.
