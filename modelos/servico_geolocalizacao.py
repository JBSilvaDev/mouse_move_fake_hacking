"""
Módulo de Serviço de Geolocalização.
Responsável por determinar a localização geográfica real do usuário utilizando
exclusivamente requisições HTTP nativas (APIs de geolocalização por rede e geocodificação),
idêntico ao funcionamento de sites e serviços web de clima e mapas.

Não executa nenhum subprocesso, terminal ou PowerShell, garantindo 100% de conformidade
e segurança para ambientes corporativos protegidos por antivírus e EDR (ex: Cortex XDR).
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime

import configuracao

def log(mensagem: str, categoria: str = "INFO"):
    """
    Função utilitária interna para emissão de logs formatados com data e hora.
    
    Args:
        mensagem (str): Texto da mensagem.
        categoria (str): Tag da categoria (ex: GEO, INFO).
    """
    hora_atual = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora_atual}] [{categoria}] {mensagem}")

class ServicoGeolocalizacao:
    """
    Serviço especializado na detecção de geolocalização via rede.
    
    Responsabilidade:
        Identificar as coordenadas (lat, lon), cidade, estado, país e IP
        utilizando requisições HTTP diretas e limpas, sem spawnar processos externos.
    """

    def obter_coordenadas_por_nome(self, nome_cidade: str):
        """
        Busca coordenadas geográficas (lat, lon) dinamicamente para um nome de cidade informado,
        utilizando a API pública de geocodificação OpenStreetMap Nominatim.
        
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
        Executa a detecção de localização geográfica real do computador via APIs HTTP:
        1. Se houver cidade manual configurada em configuracao.CIDADE_MANUAL, utiliza-a.
        2. Provedor primário via IP: ip-api.com (sem subprocessos ou PowerShell).
        3. Provedor secundário (fallback): ipwho.is.
        
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

        # 1. Verificação de cidade manual configurada (opcional para ambientes corporativos específicos)
        cidade_manual = getattr(configuracao, "CIDADE_MANUAL", None)
        if cidade_manual and isinstance(cidade_manual, str) and cidade_manual.strip():
            cidade_manual = cidade_manual.strip().upper()
            coords = self.obter_coordenadas_por_nome(cidade_manual)
            if coords:
                dados_geo["city"] = cidade_manual
                dados_geo["lat"] = round(coords[0], 4)
                dados_geo["lon"] = round(coords[1], 4)
                log(f"Localização definida via configuração manual: {cidade_manual}", "GEO")
                # Busca apenas dados complementares de rede (IP / ISP)
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
                return dados_geo

        # 2. PROVEDOR PRIMÁRIO: ip-api.com (Requisição HTTP pura)
        try:
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,isp,query"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("status") == "success":
                    dados_geo.update(data)
                    dados_geo["city"] = (dados_geo.get("city") or "DESCONHECIDA").upper()
                    dados_geo["regionName"] = (dados_geo.get("regionName") or "").upper()
                    log(f"Localização identificada via API de Rede (ip-api): {dados_geo['city']} - {dados_geo['regionName']}", "GEO")
                    return dados_geo
        except Exception as e:
            log(f"Provedor primário indisponível ({e}). Tentando provedor secundário...", "GEO")

        # 3. PROVEDOR SECUNDÁRIO (FALLBACK): ipwho.is (Requisição HTTP pura)
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
                    log(f"Localização identificada via API Secundária (ipwho.is): {dados_geo['city']}", "GEO")
                    return dados_geo
        except Exception as e:
            log(f"Provedor secundário indisponível ({e})", "GEO")

        return dados_geo
