
import os
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from datetime import datetime

# Configuración
USER = "admin"
PASS = "password"
BASE_URL = "http://138.219.60.2/api/v_2_0_3/logs/"
SAVE_PATH = "./logs_descargados"

# Crear carpeta
os.makedirs(SAVE_PATH, exist_ok=True)

# Fecha actual
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# Sesión con auth
session = requests.Session()
session.auth = HTTPBasicAuth(USER, PASS)

# Buscar carpeta de fecha
r = session.get(BASE_URL, timeout=20)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
carpetas_fecha = [a.get('href') for a in soup.find_all('a') if fecha_hoy in a.get('href', '')]
if not carpetas_fecha:
    raise Exception(f"No se encontró carpeta para la fecha {fecha_hoy}")
fecha_url = BASE_URL + carpetas_fecha[0]

# Buscar carpetas de IP
r = session.get(fecha_url, timeout=20)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
ip_carpetas = [a.get('href') for a in soup.find_all('a') if not a.get('href').startswith('?')]

# Descargar XMLs
for ip in ip_carpetas:
    ip_url = fecha_url + ip
    r = session.get(ip_url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for file in soup.find_all('a'):
        href = file.get('href')
        if href.endswith(".xml"):
            url_archivo = ip_url + href
            destino = os.path.join(SAVE_PATH, f"{ip.strip('/')}_{href}")
            print(f"Descargando: {url_archivo}")
            xml = session.get(url_archivo, timeout=20)
            with open(destino, "wb") as f:
                f.write(xml.content)
