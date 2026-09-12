import os
import re
import requests

# 1. Configuración de parámetros basados en tu información
API_URL = "https://supabase.co"
STREAM_BASE_URL = "https://cvattv.com.ar_{token}/live/c7eds/GEN__CAM1/SA_Live_dash_enc/GEN__CAM1.mpd"
OUTPUT_FILE = "lista_vs_sports.m3u"

HEADERS_STREAM = {
    "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.37",
    "Origin": "https://flow.com.py",
    "Referer": "https://flow.com.py/"
}

def obtener_token_dinamico():
    print("Obteniendo token dinámico desde la API...")
    try:
        # Hacemos la petición a la función de backend que genera las credenciales
        response = requests.get(API_URL, headers={"User-Agent": HEADERS_STREAM["User-Agent"]}, timeout=10)
        response.raise_for_status()
        
        # Intentamos parsear la respuesta como JSON
        datos = response.json()
        
        # Buscamos la clave del token (suele llamarse 'token', 'token_personal' o venir incrustada)
        # Si la API devuelve directamente una URL con el token, lo extraemos con Regex
        if isinstance(datos, dict):
            token = datos.get("token") or datos.get("strToken")
            if token:
                return token
            # Si devuelve un campo URL completo, extraemos el fragmento /tok_XYZ/
            url_incluida = datos.get("url") or datos.get("uri")
            if url_incluida:
                match = re.search(r'/tok_([^/]+)/', url_incluida)
                if match:
                    return match.group(1)
        
        # En caso de que la respuesta de la función sea texto plano o la URL directa:
        texto_respuesta = response.text
        match = re.search(r'/tok_([^/]+)/', texto_respuesta)
        if match:
            return match.group(1)
            
        print("No se pudo mapear automáticamente el formato del token. Respuesta cruda:", texto_respuesta[:200])
        return None
    except Exception as e:
        print(f"Error al conectar con la API de autenticación: {e}")
        return None

def generar_m3u(token):
    # Reemplazamos el marcador de posición por el token real obtenido
    url_final_canal = STREAM_BASE_URL.replace("{token}", token)
    
    contenido_m3u = f"""#EXTM3U

#EXTINF:-1 tvg-id="VS SPORTS" tvg-name="VS SPORTS" tvg-logo="https://googleusercontent.com" group-title="Deportes",VS SPORTS
#EXTVLCOPT:http-user-agent={HEADERS_STREAM["User-Agent"]}
#EXTVLCOPT:http-origin={HEADERS_STREAM["Origin"]}
#EXTVLCOPT:http-referrer={HEADERS_STREAM["Referer"]}
#KODIPROP:inputstream.adaptive.license_type=clearkey
#KODIPROP:inputstream.adaptive.license_key={API_URL}
{url_final_canal}
"""
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(contenido_m3u)
    print(f"¡Lista M3U actualizada con éxito en el archivo: '{OUTPUT_FILE}'!")

if __name__ == "__main__":
    token_valido = obtener_token_dinamico()
    if token_valido:
        print(f"Token localizado con éxito: {token_valido[:15]}...")
        generar_m3u(token_valido)
    else:
        print("Error: No se pudo generar el archivo M3U porque no se obtuvo un token válido.")

