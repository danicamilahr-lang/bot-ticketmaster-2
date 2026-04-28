import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = [
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-sabado-3-octubre",
    "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"
]

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def iniciar_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    return driver

def estado_evento(driver, url):
    driver.get(url)
    time.sleep(5)
    html = driver.page_source.lower()

    if "agotado" in html or "sold out" in html:
        return "AGOTADO"

    if "comprar" in html or "ver entradas" in html:
        return "DISPONIBLE"

    return "SIN_INFO"

driver = iniciar_driver()

import time

for ciclo in range(10):  # Revisa durante ~30 minutos
    print(f"Revisión #{ciclo+1}")

    for url in URLS:
        try:
            estado = estado_evento(driver, url)
            print(url, "→", estado)

            if estado == "DISPONIBLE":
                enviar_telegram(f"🚨 ENTRADAS DISPONIBLES\n{url}")

        except Exception as e:
            print("Error:", e)

    time.sleep(180)  # Espera 3 minutos entre revisiones

driver.quit()
