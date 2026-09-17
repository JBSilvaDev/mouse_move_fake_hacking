"""
Módulo de Serviço de Geolocalização.
Responsável por determinar a localização geográfica real do usuário utilizando
prioritariamente a API nativa de geolocalização do Windows (Windows Location Service / WinRT Geolocator),
idêntico ao funcionamento de aplicativos e serviços de clima do sistema operacional.
Possui fallback dinâmico para geocodificação reversa e provedores de rede (IP),
sem qualquer cidade ou coordenada fixa em código.
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
    Serviço especializado na detecção e triangulação de geolocalização do computador.
    
    Responsabilidade:
        Identificar as coordenadas reais (lat, lon) e o local (cidade, estado)
        via Windows Location Service (Wi-Fi/GPS) e geocodificação reversa,
        com fallback para serviços de IP sem valores marretados.
    """

    def reverse_geocode(self, lat: float, lon: float):
        """
        Descobre o nome da cidade e estado a partir das coordenadas geográficas (lat, lon).
        
        Args:
            lat (float): Latitude.
            lon (float): Longitude.
            
        Returns:
            tuple[str, str] | None: Tupla (cidade, estado) em letras maiúsculas ou None se falhar.
        """
        try:
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=pt"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                cidade = data.get("city") or data.get("locality")
                estado = data.get("principalSubdivision")
                if cidade:
                    return cidade.strip().upper(), (estado or "BR").strip().upper()
        except Exception:
            pass

        # Fallback de reverse geocode via OpenStreetMap Nominatim
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'AntiAusente/1.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                addr = data.get("address", {})
                cidade = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("village")
                estado = addr.get("state")
                if cidade:
                    return cidade.strip().upper(), (estado or "BR").strip().upper()
        except Exception:
            pass

        return None

    def obter_coordenadas_por_nome(self, nome_cidade: str):
        """
        Busca coordenadas geográficas (lat, lon) dinamicamente para um nome de cidade informado,
        sem atalhos fixos ou cidades marretadas.
        
        Args:
            nome_cidade (str): Nome da cidade pesquisada.
            
        Returns:
            tuple[float, float] | None: Coordenadas (lat, lon) ou None se não localizadas.
        """
        cidade_limpa = (nome_cidade or "").strip()
        if not cidade_limpa:
            return None

        try:
            termo = urllib.parse.quote(f"{cidade_limpa}, Brasil")
            url = f"https://nominatim.openstreetmap.org/search?q={termo}&format=json&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'AntiAusente/1.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data and len(data) > 0:
                    return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass
        return None

    def obter_localizacao_windows(self):
        """
        Consulta o Windows Location Service (API nativa do Windows) via WinRT Geolocator
        com triangulação Wi-Fi e sensores, exatamente como os aplicativos de clima utilizam.
        
        Returns:
            tuple[float, float] | None: Coordenadas (lat, lon) com alta precisão ou None se indisponível.
        """
        # Script PowerShell executando a API nativa do Windows Runtime (WinRT Geolocator)
        # com AsTask para resolução assíncrona robusta.
        ps_cmd = (
            "try { "
            "  [Windows.Devices.Geolocation.Geolocator, Windows.Devices.Geolocation, ContentType = WindowsRuntime] | Out-Null; "
            "  Add-Type -AssemblyName System.Runtime.WindowsRuntime; "
            "  $asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | "
            "    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | "
            "    Select-Object -First 1; "
            "  $geo = [Windows.Devices.Geolocation.Geolocator]::new(); "
            "  $op = $geo.GetGeopositionAsync(); "
            "  $task = $asTaskGeneric.MakeGenericMethod([Windows.Devices.Geolocation.Geoposition]).Invoke($null, @($op)); "
            "  if ($task.Wait(4000) -and $task.IsCompleted -and -not $task.IsFaulted) { "
            "    $pos = $task.Result.Coordinate.Point.Position; "
            "    Write-Output ($pos.Latitude.ToString([System.Globalization.CultureInfo]::InvariantCulture) + ';' + $pos.Longitude.ToString([System.Globalization.CultureInfo]::InvariantCulture)); "
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
                timeout=8.0,
                creationflags=creation_flags
            )
            for linha in proc.stdout.splitlines():
                linha = linha.strip()
                if ";" in linha:
                    partes = linha.split(";")
                    lat = float(partes[0].strip())
                    lon = float(partes[1].strip())
                    if lat != 0 and lon != 0:
                        log(f"Coordenadas obtidas via Windows Location API (Wi-Fi/GPS): {lat:.4f}, {lon:.4f}", "GPS")
                        return lat, lon
        except Exception as e:
            log(f"Windows Location indisponível ({e})", "GPS")
        return None

    def obter_cidade_windows_weather(self):
        """
        Verifica se há cidade definida na configuração de clima da barra de tarefas / Feeds do Windows.
        
        Returns:
            str | None: Nome da cidade configurada ou None.
        """
        try:
            ps_cmd = 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Feeds" -Name "ShellFeedsLocation" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ShellFeedsLocation'
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=2.0,
                creationflags=creation_flags
            )
            loc = proc.stdout.strip()
            if loc and len(loc) > 2:
                cidade = loc.split(",")[0].strip().upper()
                if cidade and cidade not in ("UNKNOWN", "LOCAL"):
                    return cidade
        except Exception:
            pass
        return None

    def obter_geolocalizacao_completa(self) -> dict:
        """
        Executa a estratégia oficial para obtenção da localização geográfica real do computador:
        1. API nativa de geolocalização do Windows (WinRT Geolocator / Wi-Fi e Sensores).
           Se disponível, realiza geocodificação reversa das coordenadas exatas.
        2. Configuração de clima/feeds do Windows (ShellFeedsLocation).
        3. Provedores de geolocalização por IP da internet (ip-api.com e ipwho.is).
        
        Returns:
            dict: Dicionário contendo cidade, estado, país, latitude, longitude, IP e ISP.
        """
        dados_geo = {
            "query": "",
            "city": "DESCONHECIDA",
            "regionName": "",
            "country": "BRASIL",
            "lat": 0.0,
            "lon": 0.0,
            "isp": ""
        }

        # 1. PRIORIDADE MÁXIMA: Windows Location Service (API nativa do Windows)
        coords_windows = self.obter_localizacao_windows()
        if coords_windows:
            lat_win, lon_win = coords_windows
            dados_geo["lat"] = round(lat_win, 4)
            dados_geo["lon"] = round(lon_win, 4)

            rev = self.reverse_geocode(lat_win, lon_win)
            if rev:
                cidade_rev, estado_rev = rev
                dados_geo["city"] = cidade_rev
                dados_geo["regionName"] = estado_rev
                log(f"Localização real identificada via Windows Location API: {cidade_rev}, {estado_rev}", "GPS")

            # Coleta dados complementares de rede (IP e Provedor) sem sobrescrever as coordenadas do Windows
            try:
                url = "http://ip-api.com/json/?fields=status,country,query,isp"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data_net = json.loads(resp.read().decode())
                    if data_net.get("status") == "success":
                        if data_net.get("query"):
                            dados_geo["query"] = data_net.get("query")
                        if data_net.get("isp"):
                            dados_geo["isp"] = data_net.get("isp")
            except Exception:
                pass

            return dados_geo

        # 2. SEGUNDA PRIORIDADE: Clima / Feeds configurados no Windows
        cidade_clima = self.obter_cidade_windows_weather()
        if cidade_clima:
            coords = self.obter_coordenadas_por_nome(cidade_clima)
            if coords:
                dados_geo["city"] = cidade_clima
                dados_geo["lat"] = round(coords[0], 4)
                dados_geo["lon"] = round(coords[1], 4)
                log(f"Localização obtida via Configuração de Clima do Windows: {cidade_clima}", "CLIMA")
                return dados_geo

        # 3. TERCEIRA PRIORIDADE (FALLBACK): Geolocalização por IP externo
        try:
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    dados_geo.update(data)
                    dados_geo["city"] = (dados_geo.get("city") or "DESCONHECIDA").upper()
                    dados_geo["regionName"] = (dados_geo.get("regionName") or "").upper()
                    log(f"Localização aproximada obtida via IP: {dados_geo['city']}", "GEO")
                    return dados_geo
        except Exception:
            pass

        # 4. Fallback secundário por IP alternativo (ipwho.is)
        try:
            req = urllib.request.Request("https://ipwho.is/", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data_alt = json.loads(resp.read().decode())
                if data_alt.get("success") and data_alt.get("city"):
                    dados_geo["city"] = data_alt.get("city").upper()
                    dados_geo["lat"] = round(float(data_alt.get("latitude", 0.0)), 4)
                    dados_geo["lon"] = round(float(data_alt.get("longitude", 0.0)), 4)
                    dados_geo["regionName"] = data_alt.get("region_code", "").upper()
                    dados_geo["query"] = data_alt.get("ip", "")
                    dados_geo["isp"] = data_alt.get("connection", {}).get("isp", "")
                    log(f"Localização obtida via IP Alternativo: {dados_geo['city']}", "GEO")
        except Exception:
            pass

        return dados_geo
