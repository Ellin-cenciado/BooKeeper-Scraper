import os
import requests
from bs4 import BeautifulSoup

# Variables de entorno inyectadas por GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        respuesta = requests.post(url, data=data)
        respuesta.raise_for_status() # Lanza un error si el status no es 200 OK
        print(f"Ping enviado a Telegram exitosamente: {respuesta.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error al enviar el mensaje de Telegram: {e}")
        # Esto nos mostrará el motivo exacto del rechazo de Telegram
        if respuesta is not None:
            print(f"Detalle de Telegram: {respuesta.text}")

def verificar_estado_libro():
    url_destino = "http://0873.bepe.ar/cgi-bin/koha/opac-detail.pl?biblionumber=101337"
    archivo_memoria = "estado_anterior.txt"

    # Configuramos la petición para que pase por la red de proxies de ScraperAPI
    parametros = {
        'api_key': SCRAPER_API_KEY,
        'url': url_destino,
        'premium': 'true',  # Fuerza a usar IPs residenciales indetectables
        'country_code': 'ar' # Fuerza a usar IPs de Argentina
    }

    try:
        
        # Hacemos la petición a la API, pasándole la URL destino
        respuesta = requests.get('https://api.scraperapi.com/', params=parametros)
        respuesta.raise_for_status()
        
        soup = BeautifulSoup(respuesta.text, "html.parser")
        estado_elemento = soup.find("span", class_="item-status")
        
        if estado_elemento:
            estado_actual = estado_elemento.get_text(strip=True)
            print(f"Estado leído hoy a través de proxy: {estado_actual}")
            
            estado_anterior = ""
            if os.path.exists(archivo_memoria):
                with open(archivo_memoria, "r", encoding="utf-8") as f:
                    estado_anterior = f.read().strip()
            
            if estado_actual != estado_anterior:
                if "Prestado" not in estado_actual: 
                    mensaje = f"📚 ¡BUENAS NOTICIAS! El libro cambió de estado.\n\nNuevo estado: {estado_actual}\n\nLink: {url_destino}"
                    enviar_mensaje_telegram(mensaje)
                    print("¡Mensaje de Telegram enviado!")
            
            # Guardamos el estado actual
            with open(archivo_memoria, "w", encoding="utf-8") as f:
                f.write(estado_actual)
                
        else:
            print("No se encontró la etiqueta de estado. Es posible que el HTML devuelto sea diferente.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")

if __name__ == "__main__":
    verificar_estado_libro()
