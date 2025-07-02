
import os
import sqlite3
import logging
from logging.handlers import SysLogHandler
import requests
from dotenv import load_dotenv
from zeep import Client

load_dotenv("config.env")

# Logger
logger = logging.getLogger("sync_estado")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Log local
fh = logging.FileHandler("sync_estado.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Syslog
try:
    syslog_handler = SysLogHandler(address=(os.getenv("SYSLOG_HOST"), int(os.getenv("SYSLOG_PORT"))))
    syslog_handler.setFormatter(formatter)
    logger.addHandler(syslog_handler)
except Exception as e:
    logger.error(f"No se pudo conectar a Syslog: {e}")

# Autenticación y consulta a ISPCube
def obtener_clientes_ispcube():
    url_login = f"{os.getenv('ISPCUBE_BASE_URL')}/sanctum/token"
    data = {
        "username": os.getenv("ISPCUBE_USERNAME"),
        "password": os.getenv("ISPCUBE_PASSWORD")
    }
    headers_login = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api-key": os.getenv("ISPCUBE_API_KEY"),
        "client-id": os.getenv("ISPCUBE_CLIENT_ID"),
        "login-type": "api"
    }
    r = requests.post(url_login, json=data, headers=headers_login)
    r.raise_for_status()
    token = r.json()["token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api-key": os.getenv("ISPCUBE_API_KEY"),
        "client-id": os.getenv("ISPCUBE_CLIENT_ID"),
        "login-type": "api",
        "username": os.getenv("ISPCUBE_USERNAME")
    }

    url = f"{os.getenv('ISPCUBE_BASE_URL')}/customer?deleted=false&temporary=false"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# SOAP a Flowdat
def enviar_estado_flowdat(idgestion, estado):
    wsdl = os.getenv("FLOWDAT_WSDL")
    client = Client(wsdl=wsdl)
    auth = {"usuario": os.getenv("FLOWDAT_USER"), "password": os.getenv("FLOWDAT_PASS")}
    if estado == "active":
        result = client.service.activeCmcliente(auth, idgestion, "Aristóbulo")
    else:
        result = client.service.suspendedCmcliente(auth, idgestion, "Aristóbulo")
    return result

# Equivalencia de estados
estado_map = {"enabled": "active", "blocked": "suspended"}

# SQLite
conn = sqlite3.connect("clientes.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS clientes (code TEXT PRIMARY KEY, status TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS estados_previos (code TEXT PRIMARY KEY, status TEXT)")

try:
    clientes = obtener_clientes_ispcube()
    for cliente in clientes:
        code = cliente.get("code")
        status = cliente.get("status")
        if not code or status not in estado_map:
            continue
        estado_nuevo = estado_map[status]

        c.execute("INSERT OR REPLACE INTO clientes (code, status) VALUES (?, ?)", (code, estado_nuevo))
        c.execute("SELECT status FROM estados_previos WHERE code = ?", (code,))
        row = c.fetchone()

        if not row:
            c.execute("INSERT INTO estados_previos (code, status) VALUES (?, ?)", (code, estado_nuevo))
        elif row[0] != estado_nuevo:
            try:
                enviar_estado_flowdat(code, estado_nuevo)
                logger.info(f"Estado modificado para {code}: {row[0]} → {estado_nuevo}")
                c.execute("UPDATE estados_previos SET status = ? WHERE code = ?", (estado_nuevo, code))
            except Exception as e:
                logger.error(f"Error SOAP para {code}: {e}")

    conn.commit()
except Exception as e:
    logger.error(f"Error general: {e}")
finally:
    conn.close()
