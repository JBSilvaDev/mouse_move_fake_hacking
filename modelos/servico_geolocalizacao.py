"""
Módulo de Serviço de Geolocalização.
Responsável por determinar a localização geográfica real do usuário utilizando
prioritariamente a API nativa do Windows (WinRT Geolocator) via SDK em C++ (winsdk)
diretamente em memória (sem criar subprocessos ou invocar PowerShell), garantindo
alta precisão (Wi-Fi/GPS) e imunidade a bloqueios por antivírus/EDR corporativo (Cortex XDR).

Possui fallback dinâmico para geocodificação reversa e APIs de rede (IP HTTP puro).
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime

import configuracao

# Tentativa de importação do SDK nativo do Windows (in-process C++ extension)
try:
    import asyncio
    import winsdk.windows.devices.geolocation as wdg
    TEM_WINSDK = True
except ImportError:
    TEM_WINSDK = False

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
    Serviço especializado na detecção de geolocalização do computador.
    
    Responsabilidade:
        Identificar as coordenadas reais (lat, lon), cidade, estado, país e IP
        utilizando a API nativa do Windows via winsdk (in-memory) e APIs HTTP diretas,
        sem spawnar nenhum processo filho (powershell.exe ou cmd.exe).
    """

    def obter_localizacao_winsdk(self):
        """
        Consulta o Windows Location Service (Wi-Fi / Sensores) diretamente em memória C++
        via SDK oficial do Windows (winsdk), sem subprocessos ou PowerShell.
        
        Returns:
            tuple[float, float] | None: Coordenadas (lat, lon) de alta precisão ou None se indisponível.
        """
        if not TEM_WINSDK:
            return None

        async def _consultar_gps():
            try:
                # Solicita acesso ao serviço de localização do Windows
                status = await wdg.Geolocator.request_access_async()
                if status != wdg.GeolocationAccessStatus.ALLOWED:
                    log(f"Permissão de localização do Windows: {status}", "GPS")
                    return None

                locator = wdg.Geolocator()
                locator.desired_accuracy = wdg.PositionAccuracy.HIGH
                pos = await locator.get_geoposition_async()
                if pos and pos.coordinate and pos.coordinate.point:
                    coord = pos.coordinate.point.position
                    return coord.latitude, coord.longitude
            except Exception as e:
                log(f"Falha ao consultar winsdk: {e}", "GPS")
            return None

        try:
            return asyncio.run(_consultar_gps())
        except Exception as e:
            log(f"Erro no loop assíncrono do winsdk: {e}", "GPS")
            return None

    def reverse_geocode(self, lat: float, lon: float):
        """
        Descobre dinamicamente o nome da cidade e estado a partir das coordenadas geográficas (lat, lon).
        
        Args:
            lat (float): Latitude.
            lon (float): Longitude.
            
        Returns:
            tuple[str, str] | None: Tupla (cidade, estado) em maiúsculas ou None se falhar.
        """
        try:
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=pt"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                cidade = data.get("city") or data.get("locality")
                estado = data.get("principalSubdivision")
                if cidade:
                    return cidade.strip().upper(), (estado or "BR").strip().upper()
        except Exception:
            pass

        # Fallback via OpenStreetMap Nominatim
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'AntiAusente/1.0 (Python)'})
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
        utilizando a API pública OpenStreetMap Nominatim.
        
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
            req = urllib.request.Request(url, headers={'User-Agent': 'AntiAusente/1.0 (Python)'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data and len(data) > 0:
                    return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass
        return None

    def obter_geolocalizacao_completa(self) -> dict:
        """
        Executa a detecção de localização geográfica real do computador:
        1. Se houver cidade manual configurada em configuracao.CIDADE_MANUAL, utiliza-a.
        2. ALTA PRECISÃO (In-Memory): Consulta a API nativa do Windows via winsdk (Wi-Fi/GPS)
           sem executar nenhum subprocesso ou PowerShell.
        3. FALLBACK DE REDE (HTTP Puro): Consulta APIs de geolocalização por IP (ip-api.com e ipwho.is).
        
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

        # 1. Verificação de cidade manual configurada (caso o usuário deseje fixar)
        cidade_manual = getattr(configuracao, "CIDADE_MANUAL", None)
        if cidade_manual and isinstance(cidade_manual, str) and cidade_manual.strip():
            cidade_manual = cidade_manual.strip().upper()
            coords = self.obter_coordenadas_por_nome(cidade_manual)
            if coords:
                dados_geo["city"] = cidade_manual
                dados_geo["lat"] = round(coords[0], 4)
                dados_geo["lon"] = round(coords[1], 4)
                log(f"Localização definida via configuração manual: {cidade_manual}", "GEO")
                self._preencher_dados_rede(dados_geo)
                return dados_geo

        # 2. ALTA PRECISÃO: Windows Location Service via winsdk (Wi-Fi/GPS em memória)
        coords_gps = self.obter_localizacao_winsdk()
        if coords_gps:
            lat_gps, lon_gps = coords_gps
            dados_geo["lat"] = round(lat_gps, 4)
            dados_geo["lon"] = round(lon_gps, 4)
            log(f"Coordenadas de alta precisão obtidas via winsdk (Wi-Fi/GPS): {lat_gps:.4f}, {lon_gps:.4f}", "GPS")

            rev = self.reverse_geocode(lat_gps, lon_gps)
            if rev:
                cidade_rev, estado_rev = rev
                dados_geo["city"] = cidade_rev
                dados_geo["regionName"] = estado_rev
                log(f"Localização real identificada: {cidade_rev}, {estado_rev}", "GPS")

            self._preencher_dados_rede(dados_geo)
            return dados_geo

        # 3. FALLBACK DE REDE: ip-api.com (HTTP Puro, sem subprocessos)
        try:
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("status") == "success":
                    dados_geo.update(data)
                    dados_geo["city"] = (dados_geo.get("city") or "DESCONHECIDA").upper()
                    dados_geo["regionName"] = (dados_geo.get("regionName") or "").upper()
                    log(f"Localização identificada via IP de rede: {dados_geo['city']} - {dados_geo['regionName']}", "GEO")
                    return dados_geo
        except Exception as e:
            log(f"Provedor de rede primário indisponível ({e})", "GEO")

        # 4. FALLBACK SECUNDÁRIO: ipwho.is (HTTP Puro)
        try:
            req = urllib.request.Request("https://ipwho.is/", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data_alt = json.loads(resp.read().decode('utf-8'))
                if data_alt.get("success") and data_alt.get("city"):
                    dados_geo["city"] = data_alt.get("city").upper()
                    dados_geo["lat"] = round(float(data_alt.get("latitude", 0.0)), 4)
                    dados_geo["lon"] = round(float(data_alt.get("longitude", 0.0)), 4)
                    dados_geo["regionName"] = data_alt.get("region_code", "").upper()
                    dados_geo["country"] = (data_alt.get("country") or "BRASIL").upper()
                    dados_geo["query"] = data_alt.get("ip", "")
                    dados_geo["isp"] = data_alt.get("connection", {}).get("isp", "")
                    log(f"Localização identificada via IP secundário: {dados_geo['city']}", "GEO")
                    return dados_geo
        except Exception as e:
            log(f"Provedor de rede secundário indisponível ({e})", "GEO")

        return dados_geo

    def _preencher_dados_rede(self, dados_geo: dict):
        """Preenche IP público e provedor levemente via HTTP sem sobrescrever coordenadas."""
        try:
            url = "http://ip-api.com/json/?fields=status,query,isp"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data_net = json.loads(resp.read().decode('utf-8'))
                if data_net.get("query"):
                    dados_geo["query"] = data_net.get("query")
                if data_net.get("isp"):
                    dados_geo["isp"] = data_net.get("isp")
        except Exception:
            pass
