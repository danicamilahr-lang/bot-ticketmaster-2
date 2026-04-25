import requests
import hashlib
from bs4 import BeautifulSoup
import os
import json

# =========================
# TELEGRAM (SECRETS)
# =========================
TOKEN = os.getenv("8704703366:AAHErSnoVFTJUBTchB_yIz4X9pJ8dIbf8Ik")
CHAT_ID = os.getenv("7736479049")

# =========================
# URLS
# =========================
URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

# =========================
# HEADERS
# =========================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

# =========================
# TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error enviando Telegram:", e)

# =========================
# FUNCIONES
# =========================
def obtener_html(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    return r.text

def analizar_botones(html):
    soup = BeautifulSoup(html, "html.parser")
    botones = soup.find_all(["a", "button"])
    textos = [b.get_text(strip=True).lower() for b in botones]
    return textos

def estado_evento(html):
    textos = analizar_botones(html)

    if any("ver entradas" in t or "comprar" in t for t in textos):
        return "DISPONIBLE"

    if any("agotado" in t for t in textos):
        return "AGOTADO"

    return "SIN_INFO"

def hash_pagina(html):
    limpio = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    return hashlib.md5(limpio.encode()).hexdigest()

# =========================
# CARGAR ESTADO
# =========================
try:
    with open("estado.json") as f:
        estado_guardado = json.load(f)
except:
    estado_guardado = {}

# =========================
# EJECUCIÓN
# =========================
for url in URLS:
    try:
        html = obtener_html(url)

        estado_actual = estado_evento(html)
        hash_actual = hash_pagina(html)

        estado_prev = estado_guardado.get(url, {})
        estado_anterior = estado_prev.get("estado")
        hash_anterior = estado_prev.get("hash")

        print(f"{url} → {estado_actual}")

        cambio_pagina = hash_anterior != hash_actual
        cambio_importante = (
            estado_anterior == "AGOTADO" and estado_actual == "DISPONIBLE"
        )

        if cambio_pagina and cambio_importante:
            enviar_telegram(f"🚨 ENTRADAS DISPONIBLES!\n{url}")

        estado_guardado[url] = {
            "estado": estado_actual,
            "hash": hash_actual
        }

    except Exception as e:
        print(f"Error en {url}: {e}")

# =========================
# GUARDAR ESTADO
# =========================
with open("estado.json", "w") as f:
    json.dump(estado_guardado, f)
