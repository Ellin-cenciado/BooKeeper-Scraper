import cloudscraper
from bs4 import BeautifulSoup
import os

# GitHub Actions inyectará estos valores automáticamente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensaje_telegram(mensaje):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def verificar_estado_libro():
    url = "http://0873.bepe.ar/cgi-bin/koha/opac-detail.pl?biblionumber=101337"
    archivo_memoria = "estado_anterior.txt"

    # Usamos cloudscraper para imitar un navegador real y evitar el error 403
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})

    try:
        respuesta = scraper.get(url)
        respuesta.raise_for_status()
        
        soup = BeautifulSoup(respuesta.text, "html.parser")
        estado_elemento = soup.find("span", class_="item-status")
        
        if estado_elemento:
            estado_actual = estado_elemento.get_text(strip=True)
            print(f"Estado leído hoy: {estado_actual}")
            
            estado_anterior = ""
            if os.path.exists(archivo_memoria):
                with open(archivo_memoria, "r", encoding="utf-8") as f:
                    estado_anterior = f.read().strip()
            
            if estado_actual != estado_anterior:
                if "Prestado" not in estado_actual: 
                    mensaje = f"📚 ¡BUENAS NOTICIAS! El libro cambió de estado.\n\nNuevo estado: {estado_actual}\n\nLink: {url}"
                    enviar_mensaje_telegram(mensaje)
                    print("¡Mensaje de Telegram enviado!")
            
            # Guardamos el estado actual
            with open(archivo_memoria, "w", encoding="utf-8") as f:
                f.write(estado_actual)
                
        else:
            print("No se encontró la etiqueta de estado en el HTML.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estado_libro()
