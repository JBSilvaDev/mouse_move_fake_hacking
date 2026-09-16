# Anti-Ausente Hacker (Mouse Move & Ransomware Prank) 🖱️⚠️

Utilitário em Python que previne o status "Ausente" em aplicativos corporativos (como Microsoft Teams, Slack e Discord) e inclui uma tela de "Invasão Hacker / Ransomware" de alto impacto ativada por ociosidade.

---

## 📌 Sobre o Projeto

O programa executa as seguintes funções em seu computador:

1. **Anti-Ausente Inteligente:** Realiza micro-movimentos no cursor a cada **45 segundos**. O script diferencia movimentos automatizados de interações humanas, garantindo que o Teams continue "Disponível" sem interferir na contagem do tempo de ociosidade do modo hacker.
2. **Modo Invasão / Ransomware (Protetor de Tela):** Se o computador ficar inativo por **60 segundos** (sem toque humano no mouse/teclado), o script cobre todos os monitores com uma simulação realista de invasão.
3. **Desativação Exclusiva via ESC:** Durante a exibição da tela hacker, interações comuns de mouse e outras teclas são ignoradas. Somente ao pressionar a tecla **`ESC`** a tela é encerrada.
4. **Modos de Execução Flexíveis:** Permite rodar com suporte a terminal/console de depuração (`move.py`) ou em modo 100% silencioso em segundo plano (`move.pyw`).

---

## 🔥 Recursos e Elementos da Tela Hacker

- **Dados Reais da Vítima:** Extrai e exibe o **Nome do Computador** (Host) e o **Nome do Usuário logado** no Windows no topo dos comandos.
- **Contador Regressivo Ransomware:** Exibe um cronômetro regressivo (estilo extorsão) em vermelho chamativo.
- **Sons de Erro Crítico do Windows:** Utiliza a biblioteca nativa `winsound` para emitir os bipes oficiais de erro do Windows ao disparar a tela e a cada novo pop-up.
- **Zona de Exclusão Central:** Os pop-ups de erro surgem apenas na periferia/bordas da tela, mantendo o terminal central com os comandos 100% visível e desobstruído.
- **Gerenciamento Inteligente de Pop-ups (Fila FIFO):** Mantém no máximo **7 pop-ups** simultâneos na tela. A partir do 8º, a janela mais antiga é fechada automaticamente.
- **Sincronização de Progresso:** A barra de progresso avança até 95% e aguarda a exibição de todos os comandos do terminal antes de atingir 100% e iniciar o alerta piscante final.
- **Suporte Multi-Monitor:** Mapeia e cobre todas as telas conectadas ao computador.

---

## ⚙️ Requisitos e Instalação

- **Python 3.8+**
- Sistema Operacional **Windows** (necessário para `winsound`, suporte a `.pyw` e arquivos `.bat`)

### Passos para Instalação

1. Abra o terminal na pasta do projeto e crie/ative o ambiente virtual:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

```

2. Instale todas as dependências a partir do arquivo `requirements.txt`:
```powershell
pip install -r requirements.txt

```



---

## 🛠️ Modos de Execução (`.py` vs `.pyw`)

O projeto disponibiliza dois formatos de arquivo para você escolher a melhor forma de uso:

* **`move.py` (Modo Desenvolvedor / Console):** Executa exibindo a janela do terminal. Ideal para testes, depuração e acompanhamento de logs em tempo real.
* **`move.pyw` (Modo Silencioso / Produção):** Executa utilizando o `pythonw.exe`, rodando silenciosamente em segundo plano sem abrir nenhuma janela de prompt de comando (CMD).

---

## 🚀 Arquivo de Inicialização (`play.bat`)

Para facilitar a inicialização sem a necessidade de ativar o ambiente virtual manualmente pelo terminal, utilize o arquivo `play.bat`:

```bat
@echo off
start "" "venv\Scripts\pythonw.exe" "move.pyw"
exit

```

> **Dica:** Caso prefira rodar com a janela do console visível para depuração, basta alterar a segunda linha do `play.bat` para usar o arquivo `.py`:
> `start "" "venv\Scripts\python.exe" "move.py"`

---

## 💻 Como Usar

### Iniciando o programa

Dê um **duplo clique no arquivo `play.bat**`. O aplicativo entrará em execução e o ícone do projeto aparecerá na **Bandeja do Sistema (System Tray)**, próximo ao relógio do Windows.

### Encerrando a Tela Hacker

Caso a tela de invasão seja disparada, pressione a tecla **`ESC`** no teclado para fechar todas as janelas e retornar à área de trabalho.

### Encerrando o Programa Definitivamente

1. Localize o ícone da aplicação na **Bandeja do Sistema** (ao lado do relógio do Windows).
2. Clique com o **botão direito** no ícone.
3. Clique na opção **"Sair / Fechar"**.

---

## 🔧 Configurações Personalizadas

Os tempos e limites podem ser ajustados no topo dos arquivos `move.py` / `move.pyw`:

```python
# ================= CONFIGURAÇÕES =================
TEMPO_OCIOSO_ALVO = 60      # Tempo inativo (em seg) sem toque humano para ativar o modo hacker
INTERVALO_MOVER_MOUSE = 45  # Intervalo (em seg) para mover o cursor (Anti-Teams)
MAX_POPUPS = 7              # Limite máximo de janelas de pop-up simultâneas
TEMPO_CONTADOR_SEG = 180    # Tempo da contagem regressiva (180 seg = 3 minutos)
# ==================================================

```

---

## 💡 Dica de Inicialização Automática com o Windows

Para que o script inicie automaticamente sempre que ligar o computador:

1. Pressione `Win + R`, digite `shell:startup` e pressione **Enter**.
2. Cole um **Atalho** do arquivo `play.bat` dentro da pasta de Inicialização que foi aberta.
