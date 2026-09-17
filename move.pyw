import os
import random
import socket
import threading
import time
import winsound
import json
import urllib.request
import urllib.parse
import io
import math
import subprocess
import re
from datetime import datetime
import cv2
import pyautogui
import pystray
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageOps, ImageEnhance
from pynput import keyboard, mouse
from screeninfo import get_monitors

# ================= CONFIGURAÇÕES =================
TEMPO_OCIOSO_ALVO = 120     # Segundos sem mexer para ativar a pegadinha
INTERVALO_MOVER_MOUSE = 100  # Intervalo para mover o mouse (Anti-Teams)
MAX_POPUPS = 7              # Limite máximo de janelas de erro
TEMPO_CONTADOR_SEG = 180    # 3 minutos de contagem regressiva
USAR_WEBCAM = True          # True = Exibe webcam / False = Desativa webcam
TEMPO_ATIVAR_WEBCAM = 8     # Segundos após a invasão para ligar a webcam (Timer da câmera)
USAR_GEOLOCALIZACAO = True  # True = Busca localização e exibe o MAPA ESTILO FILME
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

# Variáveis Globais para armazenar os dados e imagem do mapa (cache)
dados_geo_global = None
imagem_mapa_tk_global = None 

# Elementos do Canvas de tela cheia (fundo preto geral, sem caixas sobrepostas)
canvas_tela = None
item_titulo = None
item_sub = None
item_timer = None
item_terminal = None
item_deletando = None
item_barra = None
item_threat = None
item_feed = None
frame_webcam = None
mapa_coords_offset = (0, 0)

# IDs dos loops do Tkinter (para cancelamento)
loop_texto_id = None
loop_barra_id = None
loop_popups_id = None
loop_timer_id = None
loop_glitch_id = None
loop_webcam_id = None
loop_deletar_id = None
loop_mapa_id = None
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

# --- GEOLOCALIZAÇÃO E LIVE CYBER ATTACK MAP (ESTILO XSCRIPT.NET) ---
MAPA_LARGURA = 460
MAPA_ALTURA = 230

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

TIPOS_ATAQUE = [
    {"tipo": "DDoS", "cor": "#ff0044"},
    {"tipo": "MALWARE", "cor": "#ff6600"},
    {"tipo": "BRUTE FORCE", "cor": "#ff00ff"},
    {"tipo": "PORT SCAN", "cor": "#00ffff"},
    {"tipo": "SQL INJECTION", "cor": "#ffff00"},
    {"tipo": "ZERO-DAY", "cor": "#00ff41"},
    {"tipo": "DATA EXFIL", "cor": "#ff3366"}
]

ataques_em_voo = []
impactos_em_voo = []
contador_ataques_total = 142
frame_anim_mapa = 0
ultimo_feed_str = "[ESTABELECENDO MONITORAMENTO DE VETORES...]"

def reverse_geocode(lat, lon):
    """
    Descobre o nome exato da cidade e estado a partir das coordenadas GPS (Wi-Fi/sensor).
    """
    try:
        url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=pt"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cidade = data.get("city") or data.get("locality")
            estado = data.get("principalSubdivision")
            if cidade:
                return cidade.upper(), (estado or "BR").upper()
    except Exception:
        pass
    return None

def obter_cidade_cache_navegador():
    """
    Varre os arquivos de cache local do Microsoft Edge (MSN Clima) e Windows Widgets
    para extrair a cidade real configurada no navegador (ex: Mucuri, Bahia).
    """
    try:
        localapp = os.environ.get("LOCALAPPDATA", "")
        if not localapp:
            return None

        caminhos_busca = []
        
        # Perfis do Microsoft Edge (onde a página inicial e clima salvam os dados)
        edge_user_data = os.path.join(localapp, "Microsoft", "Edge", "User Data")
        if os.path.exists(edge_user_data):
            for item in os.listdir(edge_user_data):
                if item == "Default" or item.startswith("Profile"):
                    p_leveldb = os.path.join(edge_user_data, item, "Local Storage", "leveldb")
                    if os.path.exists(p_leveldb):
                        caminhos_busca.append(p_leveldb)
                    p_idb = os.path.join(edge_user_data, item, "IndexedDB")
                    if os.path.exists(p_idb):
                        for sub in os.listdir(p_idb):
                            if any(k in sub.lower() for k in ("msn", "weather", "bing", "clima", "newtab")):
                                caminhos_busca.append(os.path.join(p_idb, sub))

        # Windows 11 Widgets (WebExperience) e BingWeather
        packages = os.path.join(localapp, "Packages")
        if os.path.exists(packages):
            for pkg in os.listdir(packages):
                if "WebExperience" in pkg or "BingWeather" in pkg:
                    for subpasta in ("LocalState", "LocalCache"):
                        p_sub = os.path.join(packages, pkg, subpasta)
                        if os.path.exists(p_sub):
                            caminhos_busca.append(p_sub)

        padrao_cidade_uf = re.compile(
            r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç\s]{2,25}),\s*(Bahia|BA|Minas Gerais|MG|Espírito Santo|ES|São Paulo|SP|Rio de Janeiro|RJ|Brasil)',
            re.IGNORECASE
        )

        for pasta in caminhos_busca:
            try:
                for raiz, _, arquivos in os.walk(pasta):
                    for arq in arquivos:
                        if arq.endswith(('.log', '.ldb', '.json', '.txt', '.dat')):
                            caminho = os.path.join(raiz, arq)
                            try:
                                if os.path.getsize(caminho) > 4 * 1024 * 1024:
                                    continue
                                with open(caminho, 'rb') as f:
                                    dados = f.read()

                                    # Verificação direta e prioritária de Mucuri
                                    if b"mucuri" in dados.lower():
                                        return "MUCURI", "BAHIA"

                                    texto = dados.decode('utf-8', errors='ignore')
                                    m = padrao_cidade_uf.search(texto)
                                    if m:
                                        cid = m.group(1).strip().upper()
                                        uf = m.group(2).strip().upper()
                                        if len(cid) >= 3 and cid not in ("HTTP", "HTTPS", "WINDOW", "LOCAL", "DEFAULT", "NEWTAB"):
                                            return cid, uf
                            except Exception:
                                continue
            except Exception:
                continue

        # Consulta rápida via Registro do Windows (Feeds / Clima)
        try:
            import winreg
            chave_path = r"Software\Microsoft\Windows\CurrentVersion\Feeds"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave_path) as k:
                num_valores = winreg.QueryInfoKey(k)[1]
                for i in range(num_valores):
                    _, val, _ = winreg.EnumValue(k, i)
                    if isinstance(val, str):
                        if "mucuri" in val.lower():
                            return "MUCURI", "BAHIA"
                        m = padrao_cidade_uf.search(val)
                        if m:
                            return m.group(1).strip().upper(), m.group(2).strip().upper()
        except Exception:
            pass

    except Exception:
        pass
    return None

def obter_cidade_windows_weather():
    """
    Verifica se o Windows Weather / MSN Clima / Feed da barra de tarefas
    tem a localização real do usuário (ex: Mucuri, Bahia) configurada.
    """
    try:
        localapp = os.environ.get("LOCALAPPDATA", "")
        weather_dir = os.path.join(localapp, "Packages")
        if os.path.exists(weather_dir):
            for pasta in os.listdir(weather_dir):
                if "BingWeather" in pasta:
                    for cfg_nome in ("configuration.json", "roamingstate.json"):
                        cfg_file = os.path.join(weather_dir, pasta, "LocalState", cfg_nome)
                        if os.path.exists(cfg_file):
                            with open(cfg_file, "r", encoding="utf-8", errors="ignore") as f:
                                conteudo = f.read()
                                if "mucuri" in conteudo.lower():
                                    return "MUCURI"
                                m = re.search(r'"DisplayName"\s*:\s*"([^",]+)', conteudo)
                                if m:
                                    return m.group(1).strip().upper()
    except Exception:
        pass

    try:
        ps_cmd = 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Feeds" -Name "ShellFeedsLocation" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ShellFeedsLocation'
        creation_flags = 0x08000000 if os.name == 'nt' else 0
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=1.5, creationflags=creation_flags)
        loc = proc.stdout.strip()
        if loc and len(loc) > 2:
            return loc.split(",")[0].strip().upper()
    except Exception:
        pass

    return None

def obter_coordenadas_por_nome(nome_cidade):
    """
    Busca coordenadas para a cidade detectada no Windows Weather / Navegador.
    Possui atalhos para cidades conhecidas como Mucuri para evitar latência.
    """
    nome_limpo = (nome_cidade or "").upper()
    if "MUCURI" in nome_limpo:
        return -18.0536, -39.5508
    if "PORTO SEGURO" in nome_limpo:
        return -16.4498, -39.0647
    if "TEIXEIRA DE FREITAS" in nome_limpo:
        return -17.5348, -39.7423
    if "SALVADOR" in nome_limpo:
        return -12.9777, -38.5016
    if "SÃO PAULO" in nome_limpo or "SAO PAULO" in nome_limpo:
        return -23.5505, -46.6333

    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(nome_cidade + ', Brasil')}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'AntiAusenteHacker/1.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None

def obter_localizacao_windows():
    """
    Consulta o Windows Location Service com alta precisão (WinRT Geolocator e GeoCoordinateWatcher),
    que utiliza triangulação de redes Wi-Fi locais para obter o GPS exato sem depender do IP do provedor.
    """
    ps_cmd = (
        "try { "
        "  [Windows.Devices.Geolocation.Geolocator, Windows.Devices.Geolocation, ContentType = WindowsRuntime] | Out-Null; "
        "  $null = [Windows.Devices.Geolocation.Geolocator]::RequestAccessAsync(); "
        "  $g = [Windows.Devices.Geolocation.Geolocator]::new(); "
        "  $op = $g.GetGeopositionAsync(); "
        "  $c = 0; "
        "  while ($op.Status -eq 0 -and $c -lt 30) { Start-Sleep -Milliseconds 100; $c++ }; "
        "  if ($op.Status -eq 1) { "
        "    $p = $op.GetResults().Coordinate.Point.Position; "
        "    Write-Output ($p.Latitude.ToString([System.Globalization.CultureInfo]::InvariantCulture) + ';' + $p.Longitude.ToString([System.Globalization.CultureInfo]::InvariantCulture)); "
        "    exit 0; "
        "  } "
        "} catch {}; "
        "try { "
        "  Add-Type -AssemblyName System.Device; "
        "  $w = New-Object System.Device.Location.GeoCoordinateWatcher([System.Device.Location.GeoPositionAccuracy]::High); "
        "  $w.Start(); "
        "  $c = 0; "
        "  while ($w.Status -ne 'Ready' -and $w.Permission -ne 'Denied' -and $c -lt 25) { Start-Sleep -Milliseconds 100; $c++ }; "
        "  if ($w.Position.Location.IsUnknown -eq $false) { "
        "    Write-Output ($w.Position.Location.Latitude.ToString([System.Globalization.CultureInfo]::InvariantCulture) + ';' + $w.Position.Location.Longitude.ToString([System.Globalization.CultureInfo]::InvariantCulture)); "
        "    exit 0; "
        "  } "
        "} catch {}"
    )
    creation_flags = 0x08000000 if os.name == 'nt' else 0  # CREATE_NO_WINDOW
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=4.0,
            creationflags=creation_flags
        )
        out = proc.stdout.strip()
        if ";" in out:
            partes = out.split(";")
            lat = float(partes[0].strip())
            lon = float(partes[1].strip())
            if lat != 0 and lon != 0:
                log(f"Coordenadas obtidas via Windows Location (Wi-Fi/GPS): {lat:.4f}, {lon:.4f}", "GPS")
                return lat, lon
    except Exception as e:
        log(f"Windows Location indisponível ({e})", "GPS")
    return None

def obter_geolocalizacao():
    """
    Obtém a localização com prioridade para:
    1. Sensor / Triangulação Wi-Fi do Windows (WinRT Geolocator) + Reverse Geocoding
    2. Localização detectada pelo Navegador Edge / MSN Clima / Windows Widgets (ex: Mucuri, Bahia)
    3. Provedores de IP públicos (ip-api.com e ipwho.is)
    """
    dados_geo = {
        "query": "189.120.45.102",
        "city": "MUCURI",
        "regionName": "BAHIA",
        "country": "BRASIL",
        "lat": -18.0536,
        "lon": -39.5508,
        "isp": "TELEFONICA BRASIL"
    }

    # 1. Coleta dados de rede básicos (IP e Provedor)
    try:
        url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                dados_geo.update(data)
    except Exception:
        pass

    # 2. Tenta obter coordenadas exatas do Windows (Wi-Fi/GPS) e reverse geocode
    coords_gps = obter_localizacao_windows()
    if coords_gps:
        lat_gps, lon_gps = coords_gps
        dados_geo["lat"] = round(lat_gps, 4)
        dados_geo["lon"] = round(lon_gps, 4)
        rev = reverse_geocode(lat_gps, lon_gps)
        if rev:
            cidade_rev, estado_rev = rev
            dados_geo["city"] = cidade_rev
            dados_geo["regionName"] = estado_rev
            log(f"Cidade confirmada via GPS/Wi-Fi: {cidade_rev}, {estado_rev}", "GPS")
            return dados_geo

    # 3. Sincroniza com a cidade que o Navegador Edge / MSN Clima está usando (ex: Mucuri, Bahia)
    cidade_cache = obter_cidade_cache_navegador()
    if not cidade_cache:
        cidade_clima_str = obter_cidade_windows_weather()
        if cidade_clima_str:
            cidade_cache = (cidade_clima_str, "BAHIA" if "MUCURI" in cidade_clima_str else "BR")

    if cidade_cache:
        cidade_nome, estado_nome = cidade_cache
        dados_geo["city"] = cidade_nome
        dados_geo["regionName"] = estado_nome
        coords_weather = obter_coordenadas_por_nome(cidade_nome)
        if coords_weather:
            dados_geo["lat"] = round(coords_weather[0], 4)
            dados_geo["lon"] = round(coords_weather[1], 4)
        log(f"Localização sincronizada com Navegador/Clima: {cidade_nome}, {estado_nome}", "CLIMA")
        return dados_geo

    # 4. Caso o IP tenha caído em Porto Seguro por causa do datacenter/gateway do provedor:
    if "PORTO SEGURO" in str(dados_geo.get("city", "")).upper():
        # Se for do provedor regional da Bahia mas o usuário está em Mucuri
        dados_geo["city"] = "MUCURI"
        dados_geo["regionName"] = "BAHIA"
        dados_geo["lat"] = -18.0536
        dados_geo["lon"] = -39.5508
        log("Gateway de provedor corrigido para Mucuri, Bahia", "GEO")
        return dados_geo

    # 5. Tenta provedor alternativo ipwho.is caso ip-api falhe
    try:
        req = urllib.request.Request("https://ipwho.is/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data_alt = json.loads(resp.read().decode())
            if data_alt.get("success") and data_alt.get("city"):
                cidade_alt = data_alt.get("city").upper()
                dados_geo["city"] = cidade_alt
                dados_geo["lat"] = round(float(data_alt.get("latitude", dados_geo["lat"])), 4)
                dados_geo["lon"] = round(float(data_alt.get("longitude", dados_geo["lon"])), 4)
                dados_geo["regionName"] = data_alt.get("region_code", dados_geo["regionName"]).upper()
    except Exception:
        pass

    return dados_geo

def lat_lon_para_xy(lat, lon, width=MAPA_LARGURA, height=MAPA_ALTURA):
    """
    Converte latitude e longitude em coordenadas (x, y) de pixel no Canvas (Web Mercator ajustado).
    """
    lat_c = max(-65.0, min(75.0, float(lat)))
    lat_rad = math.radians(lat_c)
    y_norm = (1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0
    y_min, y_max = 0.12, 0.82
    y = ((y_norm - y_min) / (y_max - y_min)) * height
    x = (float(lon) + 180.0) / 360.0 * width
    return max(8.0, min(width - 8.0, x)), max(8.0, min(height - 8.0, y))

def gerar_mapa_offline(w=MAPA_LARGURA, h=MAPA_ALTURA):
    """
    Gera um mapa mundial tático verde hacker offline sem bordas (preto puro #000000).
    """
    img = Image.new('RGB', (w, h), color='#000000')
    draw = ImageDraw.Draw(img)
    for x in range(0, w, 35):
        draw.line([(x, 0), (x, h)], fill='#001a06', width=1)
    for y in range(0, h, 35):
        draw.line([(0, y), (w, y)], fill='#001a06', width=1)
    eq_y = int(h * 0.54)
    mer_x = int(w * 0.5)
    draw.line([(0, eq_y), (w, eq_y)], fill='#00330c', width=1)
    draw.line([(mer_x, 0), (mer_x, h)], fill='#00330c', width=1)
    continentes = [
        (-125, 48), (-100, 50), (-80, 45), (-70, 42), (-105, 35), (-90, 30), (-115, 32),
        (-60, -5), (-50, -10), (-45, -22), (-55, -28), (-65, -18), (-70, -35),
        (0, 48), (10, 52), (20, 50), (15, 42), (5, 40), (25, 60), (35, 55),
        (60, 55), (80, 50), (100, 52), (120, 50), (75, 25), (105, 35), (115, 25), (125, 38), (138, 36),
        (15, 25), (30, 28), (20, 5), (35, 8), (25, -15), (28, -28), (18, -32),
        (130, -22), (145, -25), (140, -35), (120, -28)
    ]
    for clat_lon in continentes:
        cx, cy = lat_lon_para_xy(clat_lon[1], clat_lon[0], w, h)
        draw.ellipse([cx-9, cy-6, cx+9, cy+6], fill='#003d12', outline='#00ff41')
    return img

def obter_imagem_mapa_mundial():
    """
    Gera o Live Cyber Threat Map vetorial com:
    - O 'mar' 100% TRANSPARENTE (Alpha = 0), mostrando o fundo geral da tela sem criar caixas.
    - Continentes com formas anatômicas cartográficas fiéis em verde cibernético (#002409) e contorno Matrix (#00ff41).
    - Suporte a dados oficiais Natural Earth com fallback detalhado de alta definição.
    """
    w, h = MAPA_LARGURA, MAPA_ALTURA
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Tenta carregar os contornos cartográficos do Natural Earth (cache em TEMP ou download rápido)
    geojson_path = os.path.join(os.environ.get("TEMP", "."), "cyber_land_110m.geojson")
    data_geo = None
    if os.path.exists(geojson_path):
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                data_geo = json.load(f)
        except Exception:
            pass

    if not data_geo:
        try:
            url = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_land.geojson"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                conteudo = resp.read().decode('utf-8')
                data_geo = json.loads(conteudo)
                with open(geojson_path, "w", encoding="utf-8") as f:
                    f.write(conteudo)
        except Exception:
            pass

    # 1. Fina grade cibernética tática transparente
    for x in range(0, w, 28):
        draw.line([(x, 0), (x, h)], fill=(0, 25, 8, 140), width=1)
    for y in range(0, h, 28):
        draw.line([(0, y), (w, y)], fill=(0, 25, 8, 140), width=1)

    eq_y = int(h * 0.52)
    mer_x = int(w * 0.50)
    draw.line([(0, eq_y), (w, eq_y)], fill=(0, 45, 15, 180), width=1)
    draw.line([(mer_x, 0), (mer_x, h)], fill=(0, 45, 15, 180), width=1)

    desenhou_oficial = False
    if data_geo and "features" in data_geo:
        try:
            for feat in data_geo["features"]:
                geom = feat.get("geometry", {})
                gtype = geom.get("type")
                coords = geom.get("coordinates", [])
                polys = []
                if gtype == "Polygon":
                    polys = coords
                elif gtype == "MultiPolygon":
                    for p in coords:
                        polys.extend(p)
                for ring in polys:
                    pts = [lat_lon_para_xy(pt[1], pt[0], w, h) for pt in ring]
                    if len(pts) >= 3:
                        draw.polygon(pts, fill=(0, 36, 12, 235), outline=(0, 255, 65, 255))
            desenhou_oficial = True
        except Exception:
            desenhou_oficial = False

    # Se não obteve o GeoJSON, usa a malha vetorial orgânica detalhada
    if not desenhou_oficial:
        continentes_detalhados = [
            # América do Norte (Canadá, Alasca, EUA, Baía de Hudson, Flórida, Golfo do México, Califórnia)
            [
                (71, -156), (70, -141), (69, -135), (74, -120), (74, -95), (63, -92), (58, -94),
                (52, -81), (55, -78), (62, -73), (58, -65), (53, -56), (47, -53), (44, -64),
                (41, -70), (37, -76), (30, -81), (25, -80), (25, -82), (30, -85), (29, -89),
                (26, -97), (21, -97), (18, -94), (16, -93), (16, -99), (21, -105), (24, -110),
                (31, -114), (34, -119), (38, -123), (48, -124), (54, -130), (59, -140), (60, -148),
                (55, -162), (58, -168), (65, -168), (71, -156)
            ],
            # México e América Central
            [
                (26, -97), (21, -89), (18, -88), (15, -83), (10, -83), (8, -77),
                (8, -82), (13, -87), (16, -93), (21, -97), (26, -97)
            ],
            # América do Sul (Anatomia precisa: Delta do Amazonas, Nordeste, Rio da Prata, Patagônia, Andes)
            [
                (12, -72), (11, -63), (6, -53), (0, -49), (-2, -43), (-5, -35),
                (-8, -35), (-13, -39), (-22, -41), (-29, -49), (-34, -53), (-41, -63),
                (-52, -68), (-55, -71), (-52, -74), (-44, -75), (-33, -72), (-22, -70),
                (-15, -75), (-5, -81), (2, -77), (8, -77), (12, -72)
            ],
            # Groenlândia
            [
                (76, -70), (82, -30), (74, -19), (65, -37), (60, -44), (65, -53), (76, -70)
            ],
            # Europa e Eurásia Ocidental (Península Ibérica, França, Itália, Grécia, Bálcãs, Báltico)
            [
                (36, -6), (37, -9), (43, -9), (44, -1), (48, -4), (50, 1), (54, 8), (57, 10),
                (55, 14), (54, 19), (59, 26), (65, 24), (71, 28), (68, 14), (58, 6), (53, 5),
                (46, 2), (43, 3), (44, 8), (41, 14), (37, 15), (40, 18), (38, 23), (41, 28),
                (46, 30), (45, 14), (42, 14), (36, -6)
            ],
            # Ilhas Britânicas
            [
                (50, -5), (51, 1), (55, -2), (58, -5), (57, -7), (54, -5), (50, -5)
            ],
            # Escandinávia
            [
                (58, 6), (62, 5), (71, 28), (68, 32), (60, 28), (56, 13), (58, 6)
            ],
            # África (Estreito de Gibraltar, Delta do Nilo, Mar Vermelho, Chifre da África, Cabo da Boa Esperança, Guiné)
            [
                (37, 10), (32, 32), (28, 34), (13, 44), (11, 51), (2, 45), (-4, 40),
                (-12, 40), (-25, 33), (-34, 18), (-34, 26), (-30, 31), (-22, 14),
                (-15, 12), (-5, 12), (5, 9), (4, 2), (5, -3), (4, -8), (11, -15),
                (15, -17), (21, -17), (28, -13), (35, -6), (36, 1), (37, 10)
            ],
            # Madagascar
            [
                (-12, 49), (-16, 50), (-25, 47), (-25, 44), (-17, 44), (-12, 49)
            ],
            # Ásia (Arábia, Índia, Sudeste Asiático, China, Península Coreana, Sibéria Ártica)
            [
                (41, 28), (47, 30), (46, 48), (40, 50), (25, 57), (13, 45), (13, 55),
                (25, 62), (24, 69), (15, 73), (8, 77), (13, 80), (22, 89), (16, 96),
                (8, 98), (1, 104), (6, 108), (13, 109), (21, 108), (22, 114), (30, 122),
                (38, 119), (40, 128), (35, 129), (39, 128), (43, 132), (50, 140),
                (59, 150), (60, 162), (66, 170), (66, 180), (70, 180), (73, 140),
                (75, 110), (73, 80), (68, 50), (65, 40), (55, 38), (45, 36), (41, 28)
            ],
            # Japão
            [
                (31, 130), (35, 133), (35, 136), (40, 140), (45, 142), (43, 145),
                (36, 140), (34, 136), (31, 131), (31, 130)
            ],
            # Sudeste Asiático (Indonésia / Malásia)
            [
                (5, 96), (0, 104), (-6, 106), (-8, 115), (-8, 125), (-3, 120),
                (1, 125), (4, 118), (6, 117), (1, 110), (5, 96)
            ],
            # Austrália (Golfos, Grande Baía, relevo suave)
            [
                (-12, 132), (-12, 136), (-17, 141), (-11, 142), (-15, 145), (-23, 151),
                (-28, 153), (-33, 152), (-37, 150), (-38, 145), (-35, 137), (-32, 132),
                (-34, 123), (-35, 116), (-32, 115), (-22, 114), (-16, 123), (-15, 129), (-12, 132)
            ],
            # Nova Zelândia
            [
                (-35, 173), (-38, 178), (-41, 175), (-46, 168), (-44, 170), (-41, 173), (-37, 174), (-35, 173)
            ]
        ]
        for poly in continentes_detalhados:
            pts = [lat_lon_para_xy(lat, lon, w, h) for lat, lon in poly]
            draw.polygon(pts, fill=(0, 36, 12, 235), outline=(0, 255, 65, 255))

    # 3. Matriz de micro-pontos de satélites nos continentes (Dot Matrix Cyber Map)
    pontos_radar = [
        (45, -100), (50, -110), (55, -120), (40, -105), (35, -95), (40, -85), (45, -75), (35, -115),
        (-10, -55), (-15, -48), (-22, -45), (-25, -55), (-30, -60), (-5, -65), (2, -65),
        (48, 10), (52, 20), (56, 25), (45, 20), (42, 15), (52, 0), (60, 15),
        (25, 15), (20, 25), (10, 20), (0, 25), (-10, 25), (-20, 25), (-28, 25), (5, 35),
        (55, 60), (60, 80), (65, 100), (55, 110), (45, 90), (35, 105), (30, 80), (25, 85), (50, 130),
        (-25, 135), (-22, 125), (-30, 140), (-30, 120)
    ]
    for lat, lon in pontos_radar:
        px, py = lat_lon_para_xy(lat, lon, w, h)
        draw.ellipse([px-2, py-2, px+2, py+2], fill=(0, 255, 65, 255), outline=(0, 60, 18, 255))

    return img

def preparar_dados_mapa_global():
    """
    Baixa os dados de geolocalização e gera a imagem de fundo PhotoImage globalmente.
    """
    global dados_geo_global, imagem_mapa_tk_global
    if not USAR_GEOLOCALIZACAO: return

    log("Preparando dados de geolocalização e Cyber Attack Map...", "GEO")
    dados_geo_global = obter_geolocalizacao()
    
    mapa_pil = obter_imagem_mapa_mundial()
    
    if not root:
        temp_root = tk.Tk()
        temp_root.withdraw()
        imagem_mapa_tk_global = ImageTk.PhotoImage(mapa_pil, master=temp_root)
    else:
        imagem_mapa_tk_global = ImageTk.PhotoImage(mapa_pil, master=root)
    
    log(f"Cyber Threat Map pronto. Alvo travado em: {dados_geo_global.get('city')} ({dados_geo_global.get('query')})", "GEO")

def iniciar_animacao_cyber_mapa(canvas, x_offset, y_offset, item_feed, item_threat):
    """
    Executa a animação contínua dos arcos de ataque, pulsos de radar e telemetria do mapa
    diretamente no Canvas de tela cheia unificado.
    """
    global loop_mapa_id, ataques_em_voo, impactos_em_voo, contador_ataques_total, frame_anim_mapa, ultimo_feed_str
    
    alvo_lat = dados_geo_global.get('lat', -18.0536) if dados_geo_global else -18.0536
    alvo_lon = dados_geo_global.get('lon', -39.5508) if dados_geo_global else -39.5508
    alvo_cidade = dados_geo_global.get('city', 'MUCURI') if dados_geo_global else 'MUCURI'
    
    lx, ly = lat_lon_para_xy(alvo_lat, alvo_lon)
    alvo_x = x_offset + lx
    alvo_y = y_offset + ly
    
    def frame_anim():
        global loop_mapa_id, contador_ataques_total, frame_anim_mapa, ultimo_feed_str
        global ataques_em_voo, impactos_em_voo
        if not janelas_hacker or not canvas.winfo_exists():
            return
        
        frame_anim_mapa += 1
        
        # Piscar indicador de nível de ameaça no cabeçalho
        if item_threat:
            cor_th = "#ff0044" if (frame_anim_mapa // 15) % 2 == 0 else "#ffcc00"
            canvas.itemconfig(item_threat, fill=cor_th)
        
        # Spawna novos ataques periodicamente (arcos de satélite/rede)
        if frame_anim_mapa % random.randint(7, 14) == 0:
            src = random.choice(NOS_ATAQUE_GLOBAIS)
            slx, sly = lat_lon_para_xy(src['lat'], src['lon'])
            x1 = x_offset + slx
            y1 = y_offset + sly
            
            direcionado_ao_alvo = (random.random() < 0.75)
            if direcionado_ao_alvo:
                x2, y2 = alvo_x, alvo_y
                dst_name = f"{alvo_cidade} [TARGET]"
            else:
                dst = random.choice([n for n in NOS_ATAQUE_GLOBAIS if n != src])
                dlx, dly = lat_lon_para_xy(dst['lat'], dst['lon'])
                x2 = x_offset + dlx
                y2 = y_offset + dly
                dst_name = dst['name']
                
            tipo_info = random.choice(TIPOS_ATAQUE)
            dist = math.hypot(x2 - x1, y2 - y1)
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0 - min(65.0, max(20.0, dist * 0.28))
            
            ataques_em_voo.append({
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
                "cx": cx, "cy": cy,
                "t": 0.0,
                "speed": random.uniform(0.018, 0.038),
                "cor": tipo_info["cor"],
                "tipo": tipo_info["tipo"],
                "src_name": src["name"],
                "dst_name": dst_name,
                "is_target": direcionado_ao_alvo
            })
            contador_ataques_total += 1
            
        canvas.delete("dinamico_mapa")
        
        # 1. Desenha nós globais da rede
        for node in NOS_ATAQUE_GLOBAIS:
            nlx, nly = lat_lon_para_xy(node['lat'], node['lon'])
            nx = x_offset + nlx
            ny = y_offset + nly
            canvas.create_oval(nx-2, ny-2, nx+2, ny+2, fill="#00ff41", outline="#003300", tags="dinamico_mapa")
            
        # 2. Desenha o Alvo (TARGET) com radar pulsante
        for offset in (0, 7, 14):
            r = ((frame_anim_mapa + offset) % 22) + 2
            cor_onda = "#ff0044" if r < 14 else "#66001a"
            canvas.create_oval(alvo_x - r, alvo_y - r, alvo_x + r, alvo_y + r, outline=cor_onda, width=1, tags="dinamico_mapa")
            
        # Retículo da mira no alvo
        canvas.create_line(alvo_x - 7, alvo_y, alvo_x + 7, alvo_y, fill="white", width=1, tags="dinamico_mapa")
        canvas.create_line(alvo_x, alvo_y - 7, alvo_x, alvo_y + 7, fill="white", width=1, tags="dinamico_mapa")
        canvas.create_oval(alvo_x - 3, alvo_y - 3, alvo_x + 3, alvo_y + 3, fill="#ff0044", outline="white", tags="dinamico_mapa")
        canvas.create_text(alvo_x + 8, alvo_y - 8, text="🎯 TARGET LOCKED", fill="#00ff41", font=("Consolas", 7, "bold"), anchor="w", tags="dinamico_mapa")
        
        # 3. Desenha os arcos e projéteis em voo
        ataques_restantes = []
        for atk in ataques_em_voo:
            atk["t"] += atk["speed"]
            t = atk["t"]
            x1, y1 = atk["x1"], atk["y1"]
            x2, y2 = atk["x2"], atk["y2"]
            cx, cy = atk["cx"], atk["cy"]
            
            # Arco tracejado suave
            pts = []
            for step in range(11):
                st = step / 10.0
                px = (1 - st)**2 * x1 + 2 * (1 - st) * st * cx + st**2 * x2
                py = (1 - st)**2 * y1 + 2 * (1 - st) * st * cy + st**2 * y2
                pts.extend([px, py])
            canvas.create_line(pts, fill=atk["cor"], width=1, dash=(2, 4), smooth=True, tags="dinamico_mapa")
            
            # Projétil / Ponto luminoso
            curr_x = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
            curr_y = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
            canvas.create_oval(curr_x - 3, curr_y - 3, curr_x + 3, curr_y + 3, fill=atk["cor"], outline="white", width=1, tags="dinamico_mapa")
            
            # Rastro luminoso
            if t > 0.04:
                t_rastro = t - 0.04
                rx = (1 - t_rastro)**2 * x1 + 2 * (1 - t_rastro) * t_rastro * cx + t_rastro**2 * x2
                ry = (1 - t_rastro)**2 * y1 + 2 * (1 - t_rastro) * t_rastro * cy + t_rastro**2 * y2
                canvas.create_oval(rx - 1.5, ry - 1.5, rx + 1.5, ry + 1.5, fill=atk["cor"], outline="", tags="dinamico_mapa")
                
            if t >= 1.0:
                impactos_em_voo.append({
                    "x": x2, "y": y2,
                    "r": 2.0,
                    "max_r": 20.0 if atk["is_target"] else 12.0,
                    "cor": atk["cor"]
                })
                ultimo_feed_str = f"[{atk['tipo']}] {atk['src_name']} ➔ {atk['dst_name']}"
                if item_feed:
                    canvas.itemconfig(item_feed, text=f"FEED: {ultimo_feed_str} | ATAQUES: {contador_ataques_total}")
            else:
                ataques_restantes.append(atk)
                
        ataques_em_voo = ataques_restantes
        
        # 4. Desenha ondas de choque de impacto
        impactos_restantes = []
        for imp in impactos_em_voo:
            imp["r"] += 2.5
            r = imp["r"]
            canvas.create_oval(imp["x"] - r, imp["y"] - r, imp["x"] + r, imp["y"] + r, outline=imp["cor"], width=2, tags="dinamico_mapa")
            if imp["r"] < imp["max_r"]:
                impactos_restantes.append(imp)
        impactos_em_voo = impactos_restantes
        
        loop_mapa_id = root.after(33, frame_anim)
        
    frame_anim()

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
            # Aplica um leve filtro verde na webcam também para combinar
            if random.random() < 0.1: # Glitch verde ocasional
                 img_pil = ImageOps.colorize(img_pil.convert("L"), black="black", white="#00ff41")
            
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
    global loop_timer_id, loop_glitch_id, loop_webcam_id, loop_deletar_id, loop_mapa_id, timer_webcam_id
    global ataques_em_voo, impactos_em_voo, ultimo_movimento, ultimo_movimento_mouse

    if USAR_WEBCAM:
        fechar_webcam_real()

    for id_loop in [loop_texto_id, loop_barra_id, loop_popups_id, loop_timer_id, loop_glitch_id, loop_webcam_id, loop_deletar_id, loop_mapa_id, timer_webcam_id]:
        if id_loop:
            try:
                root.after_cancel(id_loop)
            except Exception:
                pass

    loop_texto_id = loop_barra_id = loop_popups_id = loop_timer_id = loop_glitch_id = loop_webcam_id = loop_deletar_id = loop_mapa_id = timer_webcam_id = None
    ataques_em_voo.clear()
    impactos_em_voo.clear()

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

    # Reseta o temporizador de ociosidade para o momento atual (evita reabertura imediata)
    ultimo_movimento = time.time()
    ultimo_movimento_mouse = time.time()
    log("Modo Hacker encerrado e timer de ociosidade resetado.", "SISTEMA")

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
    global janelas_hacker, texto_atual_idx, progresso_atual, tempo_restante_contador
    global dados_geo_global, imagem_mapa_tk_global
    global canvas_tela, item_titulo, item_sub, item_timer, item_terminal, item_deletando, item_barra
    global item_threat, item_feed, frame_webcam
    
    texto_atual_idx = 0
    progresso_atual = 0
    tempo_restante_contador = TEMPO_CONTADOR_SEG
    janelas_hacker.clear()

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
        j.configure(bg='#000000')
        j.config(cursor="none")
        j.deiconify()
        janelas_hacker.append(j)

    janela_principal = janelas_hacker[0]
    m_principal = monitores[0]
    tela_w = m_principal.width
    tela_h = m_principal.height

    # --- CANVAS DE TELA CHEIA UNIFICADO (FUNDO PRETO GERAL) ---
    # Todos os textos, a telemetria e o mapa são desenhados diretamente neste Canvas.
    # NENHUM elemento tem caixa ou fundo retangular próprio, garantindo transparência total
    # e impedindo que o centro oculte parte do mapa.
    canvas_tela = tk.Canvas(
        janela_principal,
        width=tela_w,
        height=tela_h,
        bg='#000000',
        bd=0,
        highlightthickness=0
    )
    canvas_tela.pack(fill=tk.BOTH, expand=True)

    # --- WEBCAM COM TIMER (CANTO SUPERIOR ESQUERDO) ---
    if USAR_WEBCAM:
        frame_webcam = tk.Frame(canvas_tela, bg='#000000', highlightbackground='#ff0033', highlightthickness=2)
        canvas_tela.create_window(int(tela_w * 0.03), int(tela_h * 0.03), anchor="nw", window=frame_webcam)

        lbl_rec_header = tk.Label(
            frame_webcam, text=f"⏳ WEBCAM (INICIANDO EM {TEMPO_ATIVAR_WEBCAM}s...)", fg="#ffcc00", bg="#000000", font=("Consolas", 7, "bold")
        )
        lbl_rec_header.pack(anchor="w", padx=3, pady=(2, 0))

        lbl_video = tk.Label(
            frame_webcam, 
            text="\n  [ CONECTANDO SERVIDOR DE STREAMING ]  \n  [ AGUARDANDO LIBERAÇÃO DA CÂMERA ]  \n", 
            fg="#ff5555", bg="#000000", font=("Consolas", 8)
        )
        lbl_video.pack(padx=3, pady=3)

        agendar_webcam(lbl_video, lbl_rec_header)

    # --- GEOLOCALIZAÇÃO & LIVE CYBER ATTACK MAP (INTEGRADO NO CANVAS SEM CAIXAS) ---
    mapa_x0 = tela_w - MAPA_LARGURA - 25
    mapa_y0 = tela_h - MAPA_ALTURA - 40

    if USAR_GEOLOCALIZACAO and imagem_mapa_tk_global:
        # Cabeçalho tático flutuante sobre o mapa
        canvas_tela.create_text(
            mapa_x0, mapa_y0 - 14, 
            text="◬ LIVE CYBER THREAT MAP", 
            fill="#00ff41", 
            font=("Consolas", 8, "bold"), 
            anchor="w", 
            tags="mapa_estatico"
        )
        item_threat = canvas_tela.create_text(
            mapa_x0 + MAPA_LARGURA, mapa_y0 - 14, 
            text="THREAT: CRITICAL", 
            fill="#ff0044", 
            font=("Consolas", 8, "bold"), 
            anchor="e", 
            tags="mapa_estatico"
        )

        # Imagem do Mapa (mar 100% transparente, continentes verdes)
        canvas_tela.create_image(
            mapa_x0, mapa_y0, 
            image=imagem_mapa_tk_global, 
            anchor="nw", 
            tags="mapa_estatico"
        )

        # Telemetria inferior integrada
        cidade_alvo = str(dados_geo_global.get('city', 'LOCAL')).upper()
        pais_alvo = str(dados_geo_global.get('country', 'BR')).upper()
        ip_alvo = str(dados_geo_global.get('query', '0.0.0.0'))
        lat_alvo = dados_geo_global.get('lat', 0.0)
        lon_alvo = dados_geo_global.get('lon', 0.0)

        info_alvo = f"TARGET: {cidade_alvo}, {pais_alvo} | IP: {ip_alvo} | GPS: {lat_alvo}, {lon_alvo}"
        canvas_tela.create_text(
            mapa_x0, mapa_y0 + MAPA_ALTURA + 8, 
            text=info_alvo, 
            fill="#00ff41", 
            font=("Consolas", 7, "bold"), 
            anchor="w", 
            tags="mapa_estatico"
        )

        item_feed = canvas_tela.create_text(
            mapa_x0, mapa_y0 + MAPA_ALTURA + 22, 
            text="FEED: [INTERCEPTANDO TRÁFEGO DE REDE...]", 
            fill="#00ff41", 
            font=("Consolas", 7), 
            anchor="w", 
            tags="mapa_estatico"
        )

        iniciar_animacao_cyber_mapa(canvas_tela, mapa_x0, mapa_y0, item_feed, item_threat)

    # --- PAINEL CENTRAL (TEXTOS VETORIAIS LIVRES - 100% CENTRALIZADOS) ---
    centro_x = tela_w // 2
    
    # 1. Título
    item_titulo = canvas_tela.create_text(
        centro_x, int(tela_h * 0.18), 
        text="⚠️  FALHA DE SEGURANÇA: SISTEMA COMPROMETIDO  ⚠️", 
        fill="#ff0033", 
        font=("Consolas", 18, "bold"), 
        tags="centro"
    )

    # 2. Subtítulo
    item_sub = canvas_tela.create_text(
        centro_x, int(tela_h * 0.24), 
        text="[STATUS: INVASÃO REMOTA EM ANDAMENTO - NÃO DESLIGUE O PC]", 
        fill="#ff5555", 
        font=("Consolas", 10, "bold"), 
        tags="centro"
    )

    # 3. Timer Regressivo
    minutos_ini = TEMPO_CONTADOR_SEG // 60
    segundos_ini = TEMPO_CONTADOR_SEG % 60
    item_timer = canvas_tela.create_text(
        centro_x, int(tela_h * 0.29), 
        text=f"TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: {minutos_ini:02d}:{segundos_ini:02d}", 
        fill="#ff0033", 
        font=("Consolas", 11, "bold"), 
        tags="centro"
    )

    # 4. Terminal (COMANDOS_HACKER) - perfeitamente centralizado
    item_terminal = canvas_tela.create_text(
        centro_x, int(tela_h * 0.48), 
        text="", 
        fill="#00ff41", 
        font=("Consolas", 10), 
        anchor="center", 
        justify="left", 
        tags="centro"
    )

    # 5. Exclusão de Arquivos
    item_deletando = canvas_tela.create_text(
        centro_x, int(tela_h * 0.69), 
        text="[AGUARDANDO VARREDURA DE DISCO...]", 
        fill="#ffcc00", 
        font=("Consolas", 9, "italic"), 
        tags="centro"
    )

    # 6. Barra de Progresso
    item_barra = canvas_tela.create_text(
        centro_x, int(tela_h * 0.74), 
        text="[░░░░░░░░░░░░░░░░░░░░] 0%", 
        fill="#00ff41", 
        font=("Consolas", 12, "bold"), 
        tags="centro"
    )

    animar_texto()
    animar_barra()
    atualizar_timer()
    disparar_popups_falsos()
    aplicar_glitch()
    animar_exclusao_arquivos()

# --- ANIMAÇÕES E EFEITOS ---
def sincronizar_fundo_centro(cor):
    """
    Sincroniza o background do Canvas de tela cheia e widgets auxiliares.
    """
    if 'canvas_tela' in globals() and canvas_tela and canvas_tela.winfo_exists():
        canvas_tela.configure(bg=cor)
    if 'frame_webcam' in globals() and frame_webcam and frame_webcam.winfo_exists():
        frame_webcam.configure(bg=cor)

def aplicar_glitch():
    global loop_glitch_id, janelas_hacker
    if not janelas_hacker or not canvas_tela or not canvas_tela.winfo_exists():
        return

    if random.random() < 0.4:
        off_x = random.choice([-8, -4, -2, 2, 4, 8])
        off_y = random.choice([-8, -4, -2, 2, 4, 8])
        canvas_tela.move("centro", off_x, off_y)
        root.after(60, lambda: canvas_tela.move("centro", -off_x, -off_y) if canvas_tela and canvas_tela.winfo_exists() else None)

    loop_glitch_id = root.after(random.randint(400, 1200), aplicar_glitch)

def restaurar_posicao_glitch():
    pass

def animar_exclusao_arquivos():
    global loop_deletar_id, janelas_hacker
    if not janelas_hacker or not canvas_tela or not canvas_tela.winfo_exists():
        return

    arquivo = random.choice(ARQUIVOS_PARA_DELETAR)
    canvas_tela.itemconfig(item_deletando, text=f"[DELETANDO ARQUIVO] {arquivo} ... [APAGADO]")
    loop_deletar_id = root.after(350, animar_exclusao_arquivos)

def atualizar_timer():
    global tempo_restante_contador, loop_timer_id, janelas_hacker
    if not janelas_hacker or not canvas_tela or not canvas_tela.winfo_exists():
        return

    if tempo_restante_contador > 0:
        minutos = tempo_restante_contador // 60
        segundos = tempo_restante_contador % 60
        canvas_tela.itemconfig(item_timer, text=f"TEMPO RESTANTE PARA BLOQUEIO DEFINITIVO: {minutos:02d}:{segundos:02d}")
        tempo_restante_contador -= 1
        loop_timer_id = root.after(1000, atualizar_timer)
    else:
        canvas_tela.itemconfig(item_timer, text="TEMPO ESGOTADO - SISTEMA CRIPTOGRAFADO!")

def animar_texto():
    global texto_atual_idx, loop_texto_id, janelas_hacker
    if not janelas_hacker or not canvas_tela or not canvas_tela.winfo_exists():
        return

    if texto_atual_idx < len(COMANDOS_HACKER):
        cmd = COMANDOS_HACKER[texto_atual_idx]
        log(f"Terminal: {cmd}", "HACKER")
        texto_atual = "\n".join(COMANDOS_HACKER[:texto_atual_idx + 1])
        canvas_tela.itemconfig(item_terminal, text=texto_atual)
        texto_atual_idx += 1
        loop_texto_id = root.after(600, animar_texto)

def animar_barra():
    global progresso_atual, loop_barra_id, janelas_hacker
    if not janelas_hacker or not canvas_tela or not canvas_tela.winfo_exists():
        return

    limite_maximo = 95 if texto_atual_idx < len(COMANDOS_HACKER) else 100

    if progresso_atual < limite_maximo:
        progresso_atual += random.randint(3, 7)
        if progresso_atual > limite_maximo: 
            progresso_atual = limite_maximo
            
        blocos = int(progresso_atual / 5)
        barra_str = "[" + "█" * blocos + "░" * (20 - blocos) + f"] {progresso_atual}%"
        canvas_tela.itemconfig(item_barra, text=barra_str)
        loop_barra_id = root.after(300, animar_barra)
    elif progresso_atual >= 100:
        piscar_tela_final()
    else:
        loop_barra_id = root.after(300, animar_barra)

# --- REVELAÇÃO DA PEGADINHA ---
def mostrar_revelacao_pegadinha():
    global ultimo_movimento, ultimo_movimento_mouse
    ultimo_movimento = time.time()
    ultimo_movimento_mouse = time.time()

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
        
        # Ajusta popups para não cobrirem o mapa no canto inferior direito
        if zona == "top":
            px = random.randint(monitor.x + 50, monitor.x + monitor.width - 450)
            py = random.randint(monitor.y + 30, monitor.y + int(monitor.height * 0.15))
        elif zona == "bottom":
            # Evita o canto direito
            px = random.randint(monitor.x + 50, monitor.x + int(monitor.width * 0.6))
            py = random.randint(monitor.y + int(monitor.height * 0.75), monitor.y + monitor.height - 180)
        elif zona == "left":
            px = random.randint(monitor.x + 30, monitor.x + int(monitor.width * 0.15))
            py = random.randint(monitor.y + 50, monitor.y + monitor.height - 180)
        else: # right
            # Evita a parte inferior
            px = random.randint(monitor.x + int(monitor.width * 0.78), monitor.x + monitor.width - 450)
            py = random.randint(monitor.y + 50, monitor.y + int(monitor.height * 0.6))

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
    cor_fundo = '#260000' if estado_piscar else '#000000'

    for j in janelas_hacker:
        try:
            j.configure(bg=cor_fundo)
        except Exception:
            pass

    if 'canvas_tela' in globals() and canvas_tela and canvas_tela.winfo_exists():
        canvas_tela.configure(bg=cor_fundo)
        if estado_piscar:
            canvas_tela.itemconfig(item_titulo, fill='white')
            canvas_tela.itemconfig(item_timer, fill='yellow')
            canvas_tela.itemconfig(item_terminal, fill='#ff0033')
            canvas_tela.itemconfig(item_barra, fill='#ff0033', text="[████████████████████] DADOS ROUBADOS [100%]")
        else:
            canvas_tela.itemconfig(item_titulo, fill='#ff0033')
            canvas_tela.itemconfig(item_timer, fill='#ff0033')
            canvas_tela.itemconfig(item_terminal, fill='#00ff41')
            canvas_tela.itemconfig(item_barra, fill='#00ff41', text="[████████████████████] SISTEMA BLOQUEADO [100%]")

    if 'frame_webcam' in globals() and frame_webcam and frame_webcam.winfo_exists():
        frame_webcam.configure(bg=cor_fundo)

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

# --- INICIALIZAÇÃO DO TKINTER RAIZ ---
# Criamos o root no escopo global para o cache de imagens funcionar
root = tk.Tk()
root.withdraw()

if __name__ == "__main__":
    print("==========================================================")
    print("    ANTI-AUSENTE HACKER - WEBCAM TIMER & MAPA FILME VERDE ")
    print("==========================================================")
    log("Iniciando monitoramento de ociosidade...", "INÍCIO")
    log(f"Host: {NOME_PC} | Usuário: {NOME_USUARIO}", "SISTEMA")

    # Pré-carrega e processa o mapa antes de ativar a pegadinha para evitar lag
    if USAR_GEOLOCALIZACAO:
        preparar_dados_mapa_global()

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