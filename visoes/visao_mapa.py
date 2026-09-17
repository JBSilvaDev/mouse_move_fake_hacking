"""
Módulo de Visão do Live Cyber Threat Map.
Responsável por gerar o mapa mundi tático vetorial em alta definição (estilo filme de ficção/hacker),
projetar coordenadas cartográficas (Mercator) e renderizar a animação contínua
de arcos de ataque balísticos, nós globais e retículos de rastreamento no Canvas.
"""

import json
import math
import os
import random
import urllib.request
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from configuracao import MAPA_LARGURA, MAPA_ALTURA, NOS_ATAQUE_GLOBAIS, TIPOS_ATAQUE

class VisaoMapa:
    """
    Componente visual que gerencia a renderização e animação do mapa de ameaças cibernéticas.
    
    Responsabilidade:
        Desenhar o mapa vetorial com transparência no mar, traçar arcos parabólicos de ataques
        em tempo real e atualizar a telemetria do alvo e nós atacantes.
    """

    def __init__(self, largura: int = MAPA_LARGURA, altura: int = MAPA_ALTURA):
        """
        Inicializa o componente do mapa com suas dimensões.
        
        Args:
            largura (int): Largura em pixels do mapa.
            altura (int): Altura em pixels do mapa.
        """
        self.largura = largura
        self.altura = altura
        self.imagem_mapa_tk = None
        
        self.ataques_em_voo = []
        self.impactos_em_voo = []
        self.frame_anim_mapa = 0
        self.item_threat = None
        self.item_feed = None

    @staticmethod
    def lat_lon_para_xy(lat: float, lon: float, width: int = MAPA_LARGURA, height: int = MAPA_ALTURA) -> tuple[float, float]:
        """
        Converte latitude e longitude em coordenadas (x, y) de pixel no Canvas (Web Mercator ajustado).
        
        Args:
            lat (float): Latitude.
            lon (float): Longitude.
            width (int): Largura do mapa.
            height (int): Altura do mapa.
            
        Returns:
            tuple[float, float]: Coordenadas (x, y) correspondentes no Canvas.
        """
        lat_c = max(-65.0, min(75.0, float(lat)))
        lat_rad = math.radians(lat_c)
        y_norm = (1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0
        y_min, y_max = 0.12, 0.82
        y = ((y_norm - y_min) / (y_max - y_min)) * height
        x = (float(lon) + 180.0) / 360.0 * width
        return max(8.0, min(width - 8.0, x)), max(8.0, min(height - 8.0, y))

    def gerar_imagem_mapa_mundial(self) -> Image.Image:
        """
        Gera a imagem base do mapa mundial com o oceano 100% transparente (Alpha=0)
        e os continentes em tons verdes cibernéticos com contornos em verde neon.
        
        Returns:
            Image.Image: Imagem RGBA gerada pelo Pillow.
        """
        w, h = self.largura, self.altura
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Tenta carregar os contornos cartográficos do Natural Earth (cache em TEMP ou download)
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
                        pts = [self.lat_lon_para_xy(pt[1], pt[0], w, h) for pt in ring]
                        if len(pts) >= 3:
                            draw.polygon(pts, fill=(0, 36, 12, 235), outline=(0, 255, 65, 255))
                desenhou_oficial = True
            except Exception:
                desenhou_oficial = False

        # Malha de contingência caso não haja GeoJSON
        if not desenhou_oficial:
            continentes_detalhados = [
                # América do Norte
                [(71, -156), (70, -141), (69, -135), (74, -120), (74, -95), (63, -92), (58, -94),
                 (52, -81), (55, -78), (62, -73), (58, -65), (53, -56), (47, -53), (44, -64),
                 (41, -70), (37, -76), (30, -81), (25, -80), (25, -82), (30, -85), (29, -89),
                 (26, -97), (21, -97), (18, -94), (16, -93), (16, -99), (21, -105), (24, -110),
                 (31, -114), (34, -119), (38, -123), (48, -124), (54, -130), (59, -140), (60, -148),
                 (55, -162), (58, -168), (65, -168), (71, -156)],
                # México e América Central
                [(26, -97), (21, -89), (18, -88), (15, -83), (10, -83), (8, -77),
                 (8, -82), (13, -87), (16, -93), (21, -97), (26, -97)],
                # América do Sul
                [(12, -72), (11, -63), (6, -53), (0, -49), (-2, -43), (-5, -35),
                 (-8, -35), (-13, -39), (-22, -41), (-29, -49), (-34, -53), (-41, -63),
                 (-52, -68), (-55, -71), (-52, -74), (-44, -75), (-33, -72), (-22, -70),
                 (-15, -75), (-5, -81), (2, -77), (8, -77), (12, -72)],
                # Groenlândia
                [(76, -70), (82, -30), (74, -19), (65, -37), (60, -44), (65, -53), (76, -70)],
                # Europa e Eurásia Ocidental
                [(36, -6), (37, -9), (43, -9), (44, -1), (48, -4), (50, 1), (54, 8), (57, 10),
                 (55, 14), (54, 19), (59, 26), (65, 24), (71, 28), (68, 14), (58, 6), (53, 5),
                 (46, 2), (43, 3), (44, 8), (41, 14), (37, 15), (40, 18), (38, 23), (41, 28),
                 (46, 30), (45, 14), (42, 14), (36, -6)],
                # Ilhas Britânicas
                [(50, -5), (51, 1), (55, -2), (58, -5), (57, -7), (54, -5), (50, -5)],
                # África
                [(37, 10), (32, 32), (28, 34), (13, 44), (11, 51), (2, 45), (-4, 40),
                 (-12, 40), (-25, 33), (-34, 18), (-34, 26), (-30, 31), (-22, 14),
                 (-15, 12), (-5, 12), (5, 9), (4, 2), (5, -3), (4, -8), (11, -15),
                 (15, -17), (21, -17), (28, -13), (35, -6), (36, 1), (37, 10)],
                # Ásia
                [(41, 28), (47, 30), (46, 48), (40, 50), (25, 57), (13, 45), (13, 55),
                 (25, 62), (24, 69), (15, 73), (8, 77), (13, 80), (22, 89), (16, 96),
                 (8, 98), (1, 104), (6, 108), (13, 109), (21, 108), (22, 114), (30, 122),
                 (38, 119), (40, 128), (35, 129), (39, 128), (43, 132), (50, 140),
                 (59, 150), (60, 162), (66, 170), (66, 180), (70, 180), (73, 140),
                 (75, 110), (73, 80), (68, 50), (65, 40), (55, 38), (45, 36), (41, 28)],
                # Austrália
                [(-12, 132), (-12, 136), (-17, 141), (-11, 142), (-15, 145), (-23, 151),
                 (-28, 153), (-33, 152), (-37, 150), (-38, 145), (-35, 137), (-32, 132),
                 (-34, 123), (-35, 116), (-32, 115), (-22, 114), (-16, 123), (-15, 129), (-12, 132)]
            ]
            for poly in continentes_detalhados:
                pts = [self.lat_lon_para_xy(lat, lon, w, h) for lat, lon in poly]
                draw.polygon(pts, fill=(0, 36, 12, 235), outline=(0, 255, 65, 255))

        # 3. Micro-pontos nos continentes (Dot Matrix)
        pontos_radar = [
            (45, -100), (50, -110), (55, -120), (40, -105), (35, -95), (40, -85), (45, -75), (35, -115),
            (-10, -55), (-15, -48), (-22, -45), (-25, -55), (-30, -60), (-5, -65), (2, -65),
            (48, 10), (52, 20), (56, 25), (45, 20), (42, 15), (52, 0), (60, 15),
            (25, 15), (20, 25), (10, 20), (0, 25), (-10, 25), (-20, 25), (-28, 25), (5, 35),
            (55, 60), (60, 80), (65, 100), (55, 110), (45, 90), (35, 105), (30, 80), (25, 85), (50, 130),
            (-25, 135), (-22, 125), (-30, 140), (-30, 120)
        ]
        for lat, lon in pontos_radar:
            px, py = self.lat_lon_para_xy(lat, lon, w, h)
            draw.ellipse([px-2, py-2, px+2, py+2], fill=(0, 255, 65, 255), outline=(0, 60, 18, 255))

        return img

    def carregar_imagem_tk(self, master_tk: tk.Misc):
        """
        Prepara e converte a imagem base do mapa para o formato PhotoImage do Tkinter.
        
        Args:
            master_tk (tk.Misc): Widget raiz ou janela pai para ancoragem da imagem.
        """
        mapa_pil = self.gerar_imagem_mapa_mundial()
        self.imagem_mapa_tk = ImageTk.PhotoImage(mapa_pil, master=master_tk)

    def criar_elementos_mapa(self, canvas: tk.Canvas, x_offset: int, y_offset: int, dados_geo: dict):
        """
        Desenha os elementos estáticos do mapa (título, telemetria e imagem base) no Canvas.
        
        Args:
            canvas (tk.Canvas): Canvas de desenho da tela cheia.
            x_offset (int): Posição X inicial no Canvas.
            y_offset (int): Posição Y inicial no Canvas.
            dados_geo (dict): Dicionário com informações do alvo (cidade, país, IP, etc).
        """
        canvas.create_text(
            x_offset, y_offset - 14,
            text="◬ LIVE CYBER THREAT MAP",
            fill="#00ff41",
            font=("Consolas", 8, "bold"),
            anchor="w",
            tags="mapa_estatico"
        )
        self.item_threat = canvas.create_text(
            x_offset + self.largura, y_offset - 14,
            text="THREAT: CRITICAL",
            fill="#ff0044",
            font=("Consolas", 8, "bold"),
            anchor="e",
            tags="mapa_estatico"
        )

        if self.imagem_mapa_tk:
            canvas.create_image(
                x_offset, y_offset,
                image=self.imagem_mapa_tk,
                anchor="nw",
                tags="mapa_estatico"
            )

        cidade_alvo = str(dados_geo.get('city', 'LOCAL')).upper()
        pais_alvo = str(dados_geo.get('country', 'BR')).upper()
        ip_alvo = str(dados_geo.get('query', '0.0.0.0'))
        lat_alvo = dados_geo.get('lat', 0.0)
        lon_alvo = dados_geo.get('lon', 0.0)

        info_alvo = f"TARGET: {cidade_alvo}, {pais_alvo} | IP: {ip_alvo} | GPS: {lat_alvo}, {lon_alvo}"
        canvas.create_text(
            x_offset, y_offset + self.altura + 8,
            text=info_alvo,
            fill="#00ff41",
            font=("Consolas", 7, "bold"),
            anchor="w",
            tags="mapa_estatico"
        )

        self.item_feed = canvas.create_text(
            x_offset, y_offset + self.altura + 22,
            text="FEED: [INTERCEPTANDO TRÁFEGO DE REDE...]",
            fill="#00ff41",
            font=("Consolas", 7),
            anchor="w",
            tags="mapa_estatico"
        )

    def animar_passo(
        self,
        canvas: tk.Canvas,
        x_offset: int,
        y_offset: int,
        dados_geo: dict,
        ao_impactar_alvo=None
    ):
        """
        Executa um único ciclo/quadro de animação dos arcos de ataque e radares.
        
        Args:
            canvas (tk.Canvas): Canvas onde os ataques serão desenhados.
            x_offset (int): Deslocamento X da área do mapa.
            y_offset (int): Deslocamento Y da área do mapa.
            dados_geo (dict): Informações geográficas do alvo.
            ao_impactar_alvo (Callable | None): Callback invocado quando um projétil atinge o alvo.
        """
        if not canvas.winfo_exists():
            return

        self.frame_anim_mapa += 1
        alvo_lat = dados_geo.get('lat', -18.0536)
        alvo_lon = dados_geo.get('lon', -39.5508)
        alvo_cidade = dados_geo.get('city', 'MUCURI')

        lx, ly = self.lat_lon_para_xy(alvo_lat, alvo_lon, self.largura, self.altura)
        alvo_x = x_offset + lx
        alvo_y = y_offset + ly

        # Piscar indicador de ameaça no cabeçalho
        if self.item_threat:
            cor_th = "#ff0044" if (self.frame_anim_mapa // 15) % 2 == 0 else "#ffcc00"
            canvas.itemconfig(self.item_threat, fill=cor_th)

        # Spawna novos ataques periodicamente
        if self.frame_anim_mapa % random.randint(7, 14) == 0:
            src = random.choice(NOS_ATAQUE_GLOBAIS)
            slx, sly = self.lat_lon_para_xy(src['lat'], src['lon'], self.largura, self.altura)
            x1 = x_offset + slx
            y1 = y_offset + sly

            direcionado_ao_alvo = (random.random() < 0.75)
            if direcionado_ao_alvo:
                x2, y2 = alvo_x, alvo_y
                dst_name = f"{alvo_cidade} [TARGET]"
            else:
                dst = random.choice([n for n in NOS_ATAQUE_GLOBAIS if n != src])
                dlx, dly = self.lat_lon_para_xy(dst['lat'], dst['lon'], self.largura, self.altura)
                x2 = x_offset + dlx
                y2 = y_offset + dly
                dst_name = dst['name']

            tipo_info = random.choice(TIPOS_ATAQUE)
            dist = math.hypot(x2 - x1, y2 - y1)
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0 - min(65.0, max(20.0, dist * 0.28))

            self.ataques_em_voo.append({
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

        canvas.delete("dinamico_mapa")

        # 1. Desenha nós da rede global
        for node in NOS_ATAQUE_GLOBAIS:
            nlx, nly = self.lat_lon_para_xy(node['lat'], node['lon'], self.largura, self.altura)
            nx = x_offset + nlx
            ny = y_offset + nly
            canvas.create_oval(nx-2, ny-2, nx+2, ny+2, fill="#00ff41", outline="#003300", tags="dinamico_mapa")

        # 2. Desenha o Alvo com radar pulsante
        for offset in (0, 7, 14):
            r = ((self.frame_anim_mapa + offset) % 22) + 2
            cor_onda = "#ff0044" if r < 14 else "#66001a"
            canvas.create_oval(alvo_x - r, alvo_y - r, alvo_x + r, alvo_y + r, outline=cor_onda, width=1, tags="dinamico_mapa")

        canvas.create_line(alvo_x - 7, alvo_y, alvo_x + 7, alvo_y, fill="white", width=1, tags="dinamico_mapa")
        canvas.create_line(alvo_x, alvo_y - 7, alvo_x, alvo_y + 7, fill="white", width=1, tags="dinamico_mapa")
        canvas.create_oval(alvo_x - 3, alvo_y - 3, alvo_x + 3, alvo_y + 3, fill="#ff0044", outline="white", tags="dinamico_mapa")
        canvas.create_text(alvo_x + 8, alvo_y - 8, text="🎯 TARGET LOCKED", fill="#00ff41", font=("Consolas", 7, "bold"), anchor="w", tags="dinamico_mapa")

        # 3. Desenha os projéteis e arcos balísticos
        ataques_restantes = []
        for atk in self.ataques_em_voo:
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

            # Ponto luminoso
            curr_x = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
            curr_y = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
            canvas.create_oval(curr_x - 3, curr_y - 3, curr_x + 3, curr_y + 3, fill=atk["cor"], outline="white", width=1, tags="dinamico_mapa")

            if t >= 1.0:
                self.impactos_em_voo.append({
                    "x": x2, "y": y2,
                    "r": 2.0,
                    "max_r": 20.0 if atk["is_target"] else 12.0,
                    "cor": atk["cor"]
                })
                feed_msg = f"[{atk['tipo']}] {atk['src_name']} ➔ {atk['dst_name']}"
                if self.item_feed:
                    canvas.itemconfig(self.item_feed, text=f"FEED: {feed_msg}")
                if ao_impactar_alvo and atk["is_target"]:
                    ao_impactar_alvo(feed_msg)
            else:
                ataques_restantes.append(atk)

        self.ataques_em_voo = ataques_restantes

        # 4. Ondas de choque dos impactos
        impactos_restantes = []
        for imp in self.impactos_em_voo:
            imp["r"] += 2.5
            r = imp["r"]
            canvas.create_oval(imp["x"] - r, imp["y"] - r, imp["x"] + r, imp["y"] + r, outline=imp["cor"], width=2, tags="dinamico_mapa")
            if imp["r"] < imp["max_r"]:
                impactos_restantes.append(imp)
        self.impactos_em_voo = impactos_restantes

    def limpar_animacoes(self):
        """Limpa as listas de ataques e impactos em voo."""
        self.ataques_em_voo.clear()
        self.impactos_em_voo.clear()
        self.frame_anim_mapa = 0
