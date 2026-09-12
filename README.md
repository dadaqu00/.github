Para reproducir este canal correctamente en OTT Navigator usando una lista M3U, debes estructurar la información utilizando las etiquetas extendidas #EXTINF y #EXTVLCOPT. Dado que el canal utiliza protección ClearKey, es fundamental incluir las cabeceras (headers) y las credenciales de la licencia en el formato que la aplicación reconoce.Aquí tienes la estructura exacta lista para copiar:text#EXTM3UCódigo del Script (actualizar_lista.py)pythonimport os
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
Usa el código con precaución.💡 ¿Cómo usarlo en OTT Navigator de forma 100% automática?Para que no tengas que ejecutar este archivo manualmente en tu computadora cada vez que caduque el token, puedes montarlo de las siguientes maneras:Servidor Local / TV Box (Termux): Si usas Android en tu TV Box, puedes instalar la aplicación Termux, programar este script con un comando cron para que se ejecute de fondo cada determinado tiempo y guardar el archivo .m3u en el almacenamiento local de tu dispositivo. Luego, en OTT Navigator, configuras el origen de la lista apuntando a la ruta del archivo local.Hosting Gratuito (GitHub Actions / Vercel): Puedes subir este script a un repositorio privado de GitHub y usar GitHub Actions para que ejecute el archivo de Python automáticamente cada 3 o 6 horas. El script puede subir el resultado a un servidor o a una URL pública de tu propiedad, proporcionándote un enlace estático de internet que puedes poner en OTT Navigator para que la app se actualice sola. [1] (https://github.com/SeanRiggs/Automated-Playlist-EPG-Downloader)Dime si prefieres que prepare el archivo de configuración para automatizarlo en la nube con GitHub o si deseas adaptar el script para que gestione múltiples canales de Flow al mismo tiempo.GitHubGitHub - SeanRiggs/Automated-Playlist-EPG-Downloader ...Features * Automated Downloads: Pulls your playlist and EPG data directly from m3u4u.com every 24 hours. * Local Caching: The scri...FastoCloudM3U Playlist Format: EXTINF Tags and Working Examples29 jun 2026 — Table_title: M3U File Structure: The Three-Line Channel Entry Table_content: | Attribute | Purpose | Example | | --- | --- | --- |GitHubsupabase/functions-py - GitHub22 ago 2025 — Repository files navigation. README; Code of conduct; Contributing; MIT license; Security. More items. Warning. This repository ha...prepare el archivo de configuración para automatizarlo en la nube con GitHubPara automatizar la actualización de tu lista M3U de forma 100% gratuita usando la nube de GitHub, utilizaremos GitHub Actions. Esto ejecutará tu script de Python en los servidores de GitHub de forma periódica, generará el archivo .m3u actualizado y lo publicará automáticamente en una sección web pública llamada GitHub Pages.De esta forma, tendrás un enlace web directo y permanente (por ejemplo: https://github.io) que podrás configurar en OTT Navigator, olvidándote de actualizar el token de forma manual.Sigue estos 3 pasos sencillos para dejarlo todo configurado:Paso 1: El archivo de automatización (.github/workflows/actualizar.yml)Crea una carpeta en tu repositorio llamada .github y, dentro de ella, otra llamada workflows. Adentro, crea un archivo de texto llamado actualizar.yml con el siguiente contenido exacto:yamlname: Actualizar Token M3U de VS Sports

on:
  schedule:
    # Se ejecuta automáticamente cada 4 horas.
    # Puedes cambiar el "4" si notas que el token expira antes.
    - cron: '0 */4 * * *'
  workflow_dispatch: # Permite forzar la ejecución del script manualmente desde la web de GitHub

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Descargar el código del repositorio
      uses: actions/checkout@v4

    - name: Configurar entorno de Python
      uses: actions/setup-python@v5
      with:
        python-node-version: '3.10'

    - name: Instalar librerías necesarias
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: Ejecutar script de actualización
      run: python actualizar_lista.py

    - name: Guardar y subir los cambios al repositorio
      run: |
        git config --local user.email "actions@github.com"
        git config --local user.name "GitHub Actions"
        git add lista_vs_sports.m3u
        # Solo hace commit si el archivo M3U realmente cambió para evitar bucles
        git diff --quiet && git diff --staged --quiet || (git commit -m "Auto-actualización: Nuevo token generado" && git push)
Usa el código con precaución.Paso 2: Organizar tu repositorio en GitHubTu repositorio en GitHub debe contener un total de 3 archivos organizados de la siguiente estructura exacta:text📁 Tu-Repositorio
 ├── 📁 .github
 │    └── 📁 workflows
 │         └── 📄 actualizar.yml       <-- (El archivo del Paso 1)
 ├── 📄 actualizar_lista.py            <-- (El script de Python provisto en la respuesta anterior)
 └── 📄 lista_vs_sports.m3u            <-- (Puedes dejarlo en blanco, el script lo llenará solo)
Usa el código con precaución.Paso 3: Configurar los permisos y activar el enlace web (GitHub Pages)Una vez que subas los archivos a tu cuenta de GitHub, realiza estos breves ajustes en la interfaz web de tu repositorio:Permitir que el script guarde los cambios:Entra a tu repositorio en GitHub y ve a Settings (Configuración) ➡️ Actions ➡️ General.Baja hasta la sección Workflow permissions.Asegúrate de marcar la opción "Read and write permissions" y dale a Save (Guardar).Activar el enlace para tu OTT Navigator:Ve de nuevo a Settings (Configuración) ➡️ Pages (en el menú izquierdo).En la sección Build and deployment, busca la opción Source y cámbiala a Deploy from a branch.Justo abajo, en Branch, selecciona tu rama principal (normalmente se llama main o master), deja la carpeta raíz como / (root) y presiona Save.🚀 ¡Listo! ¿Cómo probarlo y usar el enlace?Prueba manual: Puedes probar si todo funciona de inmediato yendo a la pestaña Actions en tu repositorio, seleccionando el flujo "Actualizar Token M3U de VS Sports" en la barra izquierda, y haciendo clic en el botón de la derecha que dice Run workflow. Esto simulará el proceso automático.Enlace para tu OTT Navigator: Pasados unos minutos, GitHub te dará la URL pública arriba en la sección Settings ➡️ Pages. El enlace final que tendrás que escribir en tu aplicación OTT Navigator tendrá esta estructura:texthttps://[TU_USUARIO_DE_GITHUB].github.io/[NOMBRE_DE_TU_REPOSITORIO]/lista_vs_sports.m3u
