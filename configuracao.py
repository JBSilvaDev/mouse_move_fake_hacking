"""
Módulo de Configuração Geral do Sistema Anti-Ausente Hacker.
Contém parâmetros de tempo, nós globais de ataques cibernéticos, comandos de terminal
e configurações estéticas da interface gráfica.
"""

import os
import socket

# ================= TEMPOS E LIMITES =================
TEMPO_OCIOSO_ALVO = 5       # Tempo em segundos sem interação para disparar a tela hacker
INTERVALO_MOVER_MOUSE = 100   # Intervalo em segundos para movimentação preventiva do mouse (Anti-Teams)
MAX_POPUPS = 7                # Limite máximo simultâneo de janelas de erro falsas
TEMPO_CONTADOR_SEG = 180      # Duração da contagem regressiva em segundos (3 minutos)
TEMPO_ATIVAR_WEBCAM = 15      # Segundos decorridos da invasão até ligar a webcam

# ================= RECURSOS E FLAGS =================
USAR_WEBCAM = True            # Ativa ou desativa o streaming falso da webcam
USAR_GEOLOCALIZACAO = True    # Ativa ou desativa a geolocalização e o mapa mundial de ataques

# ================= IDENTIFICAÇÃO DO SISTEMA =================
NOME_USUARIO = os.getlogin().upper()
NOME_PC = socket.gethostname().upper()

# ================= DIMENSÕES DO MAPA MUNDIAL =================
MAPA_LARGURA = 460
MAPA_ALTURA = 230

# ================= SIMULAÇÃO DE EXCLUSÃO DE ARQUIVOS =================
ARQUIVOS_PARA_DELETAR = [
    f"C:\\Users\\{NOME_USUARIO}\\Desktop\\Relatorios_Financeiros_2026.xlsx",
    f"C:\\Users\\{NOME_USUARIO}\\Documents\\Fotos_Pessoais_Backup.zip",
    f"C:\\Users\\{NOME_USUARIO}\\Downloads\\Carteira_Crypto_Chaves.dat",
    f"C:\\Users\\{NOME_USUARIO}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
    f"C:\\Users\\{NOME_USUARIO}\\Documents\\Contratos_Assinados.pdf",
    f"C:\\Users\\{NOME_USUARIO}\\.ssh\\id_rsa",
    f"C:\\Windows\\System32\\drivers\\etc\\hosts"
]

# ================= COMANDOS E LOGS DO TERMINAL HACKER =================
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

# ================= NÓS GLOBAIS DE ATAQUE (CYBER THREAT MAP) =================
NOS_ATAQUE_GLOBAIS = [
    {"name": "MOSCOW", "lat": 55.7558, "lon": 37.6173, "country": "RUS"},
    {"name": "BEIJING", "lat": 39.9042, "lon": 116.4074, "country": "CHN"},
    {"name": "PYONGYANG", "lat": 39.0392, "lon": 125.7625, "country": "PRK"},
    {"name": "TEHRAN", "lat": 35.6892, "lon": 51.3890, "country": "IRN"},
    {"name": "BUCHAREST", "lat": 44.4268, "lon": 26.1025, "country": "ROU"},
    {"name": "FRANKFURT", "lat": 50.1109, "lon": 8.6821, "country": "DEU"},
    {"name": "NEW YORK", "lat": 40.7128, "lon": -74.0060, "country": "USA"},
    {"name": "LONDON", "lat": 51.5074, "lon": -0.1278, "country": "GBR"},
    {"name": "TOKYO", "lat": 35.6762, "lon": 139.6503, "country": "JPN"},
    {"name": "SINGAPORE", "lat": 1.3521, "lon": 103.8198, "country": "SGP"},
    {"name": "SYDNEY", "lat": -33.8688, "lon": 151.2093, "country": "AUS"},
    {"name": "DUBAI", "lat": 25.2048, "lon": 55.2708, "country": "ARE"},
    {"name": "TORONTO", "lat": 43.6532, "lon": -79.3832, "country": "CAN"},
    {"name": "JOHANNESBURG", "lat": -26.2041, "lon": 28.0473, "country": "ZAF"},
    {"name": "MUMBAI", "lat": 19.0760, "lon": 72.8777, "country": "IND"},
    {"name": "HONG KONG", "lat": 22.3193, "lon": 114.1694, "country": "HKG"},
    {"name": "AMSTERDAM", "lat": 52.3676, "lon": 4.9041, "country": "NLD"}
]

# ================= VETORES DE ATAQUE E CORES =================
TIPOS_ATAQUE = [
    {"tipo": "DDoS", "cor": "#ff0044"},
    {"tipo": "MALWARE", "cor": "#ff6600"},
    {"tipo": "BRUTE FORCE", "cor": "#ff00ff"},
    {"tipo": "PORT SCAN", "cor": "#00ffff"},
    {"tipo": "SQL INJECTION", "cor": "#ffff00"},
    {"tipo": "ZERO-DAY", "cor": "#00ff41"},
    {"tipo": "DATA EXFIL", "cor": "#ff3366"}
]
