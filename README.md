# Mouse Move

Pequeno utilitário em Python para movimentar o cursor periodicamente.

## Sobre

Este projeto mantém o cursor do mouse em movimento enquanto o programa estiver em execução. A cada 60 segundos, ele lê a posição atual e move o cursor para uma posição aleatória próxima, com uma variação de até 20 pixels nos eixos horizontal e vertical.

O programa permanece executando até ser interrompido manualmente com `Ctrl+C`.

## Requisitos

- Python 3.8 ou superior
- Sistema operacional com interface gráfica compatível com o PyAutoGUI
- Dependências listadas em `requirements.txt`

## Instalação

No terminal, a partir da pasta do projeto, crie e ative um ambiente virtual:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

## Uso

Execute o script com:

```powershell
python move.py
```

Quando iniciado, o programa exibe:

```text
Rodando... CTRL+C para parar
```

Para encerrar, pressione `Ctrl+C` no terminal em que o programa está rodando.

## Configuração

O intervalo entre os movimentos é definido pela constante `INTERVALO` em `move.py` e está configurado para 60 segundos:

```python
INTERVALO = 60
```

Altere esse valor, em segundos, caso precise de outra frequência.

## Funcionamento

1. Obtém a posição atual do cursor.
2. Gera deslocamentos aleatórios entre `-20` e `20` pixels para cada eixo.
3. Move o cursor para a nova posição em 0,5 segundo.
4. Aguarda o intervalo configurado e repete o processo.

O clique automático está desativado no código. A chamada `pyautogui.click()` aparece apenas como opção comentada e não é executada.

## Dependências principais

- [PyAutoGUI](https://pyautogui.readthedocs.io/): leitura da posição e movimentação do cursor.
- `MouseInfo`, `PyGetWindow`, `PyMsgBox`, `pyperclip`, `PyRect`, `PyScreeze` e `pytweening`: dependências fixadas para o funcionamento do PyAutoGUI.

## Observações

- O script precisa de acesso à sessão gráfica e ao controle do mouse.
- Ao executar, movimentos feitos pelo usuário podem ser acompanhados pelo movimento automático do programa.
- Em ambientes corporativos, verifique as políticas locais antes de usar automações de entrada.

## Licença

Nenhuma licença foi definida no repositório até o momento.