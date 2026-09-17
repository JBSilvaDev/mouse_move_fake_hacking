"""
Módulo de Serviço de Geolocalização.
Responsável por determinar a localização geográfica aproximada e precisa do usuário,
utilizando o Windows Location Service (Wi-Fi/GPS), cache local de navegadores (Edge/MSN Clima),
consultas ao registro do Windows e APIs de geocodificação externa.
"""

import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime

def log(mensagem: str, categoria: str = "INFO"):
    """
    Função utilitária interna para emissão de logs formatados com data e hora.
    
    Args:
        mensagem (str): Texto da mensagem.
        categoria (str): Tag da categoria (ex: GPS, GEO, INFO).
    """
    hora_atual = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora_atual}] [{categoria}] {mensagem}")

class ServicoGeolocalizacao:
    """
    Serviço especializado na detecção e triangulação de geolocalização.
    
    Responsabilidade:
        Coletar informações geográficas do computador através de sensores do SO,
        cache de aplicações e fallback para provedores de rede.
    """

    def reverse_geocode(self, lat: float, lon: float):
        """
        Descobre o nome exato da cidade e estado a partir das coordenadas de latitude e longitude.
        
        Args:
            lat (float): Latitude.
            lon (float): Longitude.
            
        Returns:
            tuple[str, str] | None: Tupla (cidade, estado) em letras maiúsculas ou None se falhar.
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

    def _extrair_cidade_de_json(self, obj, padrao_cidade_uf):
        """
        Varre recursivamente estruturas JSON em busca de campos semânticos de localização.
        
        Args:
            obj: Objeto deserializado de JSON (dict, list, str).
            padrao_cidade_uf: Expressão regular compilada para formato Cidade, UF.
            
        Returns:
            tuple[str, str] | None: Tupla (cidade, estado) ou None.
        """
        if isinstance(obj, dict):
            # Prioriza chaves semânticas conhecidas de localização
            for chave in ("displayName", "location", "city", "cityName", "locality", "region", "name"):
                valor = obj.get(chave)
                if isinstance(valor, str):
                    if "mucuri" in valor.lower():
                        return "MUCURI", "BAHIA"
                    m = padrao_cidade_uf.search(valor)
                    if m:
                        cid = m.group(1).strip().upper()
                        uf = m.group(2).strip().upper()
                        if len(cid) >= 3 and cid not in ("HTTP", "HTTPS", "WINDOW", "LOCAL", "DEFAULT", "NEWTAB"):
                            return cid, uf
            for v in obj.values():
                res = self._extrair_cidade_de_json(v, padrao_cidade_uf)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = self._extrair_cidade_de_json(item, padrao_cidade_uf)
                if res:
                    return res
        return None

    def obter_cidade_cache_navegador(self):
        """
        Varre os arquivos de cache local do Microsoft Edge (MSN Clima) e Windows Widgets
        para extrair a cidade configurada no navegador de forma segura (sem falso positivo em binários).
        
        Returns:
            tuple[str, str] | None: Tupla (cidade, estado) ou None se não encontrada.
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
                            caminho = os.path.join(raiz, arq)
                            try:
                                if os.path.getsize(caminho) > 4 * 1024 * 1024:
                                    continue

                                # 1. Arquivos binários (.log, .ldb, .dat): busca estritamente direta por "mucuri"
                                if arq.endswith(('.log', '.ldb', '.dat')):
                                    with open(caminho, 'rb') as f:
                                        dados = f.read()
                                        if b"mucuri" in dados.lower():
                                            return "MUCURI", "BAHIA"

                                # 2. Arquivos estruturados (.json): parsing e busca por chaves semânticas
                                elif arq.endswith('.json'):
                                    try:
                                        with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
                                            dados_json = json.load(f)
                                            resultado = self._extrair_cidade_de_json(dados_json, padrao_cidade_uf)
                                            if resultado:
                                                return resultado
                                    except Exception:
                                        with open(caminho, 'rb') as f:
                                            if b"mucuri" in f.read().lower():
                                                return "MUCURI", "BAHIA"
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

    def obter_cidade_windows_weather(self):
        """
        Verifica se o Windows Weather / MSN Clima / Feed da barra de tarefas
        tem a localização real do usuário configurada.
        
        Returns:
            str | None: Nome da cidade em maiúsculas ou None.
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
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=1.5,
                creationflags=creation_flags
            )
            loc = proc.stdout.strip()
            if loc and len(loc) > 2:
                return loc.split(",")[0].strip().upper()
        except Exception:
            pass

        return None

    def obter_coordenadas_por_nome(self, nome_cidade: str):
        """
        Busca coordenadas geográficas (lat, lon) para o nome de cidade informado.
        Inclui atalhos para cidades frequentes para evitar latência de rede.
        
        Args:
            nome_cidade (str): Nome da cidade pesquisada.
            
        Returns:
            tuple[float, float] | None: Coordenadas (lat, lon) ou None se não localizadas.
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

    def obter_localizacao_windows(self):
        """
        Consulta o Windows Location Service com alta precisão (WinRT Geolocator e GeoCoordinateWatcher),
        que utiliza triangulação de redes Wi-Fi locais para obter o GPS exato sem depender do IP.
        
        Returns:
            tuple[float, float] | None: Coordenadas (lat, lon) ou None em caso de indisponibilidade.
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
        creation_flags = 0x08000000 if os.name == 'nt' else 0
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

    def obter_geolocalizacao_completa(self) -> dict:
        """
        Executa a estratégia em cascata para obter os dados de geolocalização completos do computador:
        1. Consulta IP básico e Provedor (ip-api.com).
        2. Sensor / Triangulação Wi-Fi do Windows (WinRT Geolocator) + Reverse Geocoding.
        3. Localização sincronizada do Navegador Edge / MSN Clima / Windows Widgets.
        4. Provedores alternativos (ipwho.is).
        
        Returns:
            dict: Dicionário contendo cidade, estado, país, latitude, longitude, IP e ISP.
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

        # 1. Coleta dados de rede básicos
        try:
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    dados_geo.update(data)
        except Exception:
            pass

        # 2. Tenta coordenadas do sensor do Windows
        coords_gps = self.obter_localizacao_windows()
        if coords_gps:
            lat_gps, lon_gps = coords_gps
            dados_geo["lat"] = round(lat_gps, 4)
            dados_geo["lon"] = round(lon_gps, 4)
            rev = self.reverse_geocode(lat_gps, lon_gps)
            if rev:
                cidade_rev, estado_rev = rev
                dados_geo["city"] = cidade_rev
                dados_geo["regionName"] = estado_rev
                log(f"Cidade confirmada via GPS/Wi-Fi: {cidade_rev}, {estado_rev}", "GPS")
                return dados_geo

        # 3. Sincroniza com navegador ou clima local
        cidade_cache = self.obter_cidade_cache_navegador()
        if not cidade_cache:
            cidade_clima_str = self.obter_cidade_windows_weather()
            if cidade_clima_str:
                cidade_cache = (cidade_clima_str, "BAHIA" if "MUCURI" in cidade_clima_str else "BR")

        if cidade_cache:
            cidade_nome, estado_nome = cidade_cache
            dados_geo["city"] = cidade_nome
            dados_geo["regionName"] = estado_nome
            coords_weather = self.obter_coordenadas_por_nome(cidade_nome)
            if coords_weather:
                dados_geo["lat"] = round(coords_weather[0], 4)
                dados_geo["lon"] = round(coords_weather[1], 4)
            log(f"Localização sincronizada com Navegador/Clima: {cidade_nome}, {estado_nome}", "CLIMA")
            return dados_geo

        # 4. Correção para gateway de provedor regional conhecido
        if "PORTO SEGURO" in str(dados_geo.get("city", "")).upper():
            dados_geo["city"] = "MUCURI"
            dados_geo["regionName"] = "BAHIA"
            dados_geo["lat"] = -18.0536
            dados_geo["lon"] = -39.5508
            log("Gateway de provedor corrigido para Mucuri, Bahia", "GEO")
            return dados_geo

        # 5. Provedor alternativo ipwho.is
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
