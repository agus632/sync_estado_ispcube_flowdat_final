
import os
import sqlite3
import logging
import subprocess
from logging.handlers import SysLogHandler
import requests
from dotenv import load_dotenv

load_dotenv("config.env")

logging.basicConfig(
    level=logging.DEBUG,  # <-- DEBUG muestra TODO
    format="%(asctime)s [%(levelname)s] %(message)s"
    )

# Logger
logger = logging.getLogger("sync_estado")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Log local
fh = logging.FileHandler("sync_estado.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Logger de cambios en la base de datos
clientes_logger = logging.getLogger("clientes_log")
clientes_logger.setLevel(logging.INFO)
clientes_fh = logging.FileHandler("clientes.log")
clientes_fh.setFormatter(formatter)
clientes_logger.addHandler(clientes_fh)

# Logger de mensajes SOAP
soap_logger = logging.getLogger("soap_log")
soap_logger.setLevel(logging.INFO)
soap_fh = logging.FileHandler("soap.log")
soap_fh.setFormatter(formatter)
soap_logger.addHandler(soap_fh)

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

    url = f"{os.getenv('ISPCUBE_BASE_URL')}/customers/customers_list"
    limit = int(os.getenv("ISPCUBE_LIMIT", "100"))
    offset = 0
    todos = []

    try:
        while True:
            paged_url = f"{url}?limit={limit}&offset={offset}"
            resp = requests.get(paged_url, headers=headers)
            resp.raise_for_status()
            #data = None
            
            try:
                data = resp.json()
            except ValueError:
                logging.error("Respuesta no es JSON válido (posible 204/empty body)")
                #break

                logging.debug(f"Keys JSON: {list(data.keys()) if isinstance(data, dict) else 'lista' if data is not None else 'None'}")
            if data is None:
    	        items = []
       	    elif isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                payload = data.get("data", data)
                if payload is None:
                    items = []
                elif isinstance(payload, list):
                    items = payload
                elif isinstance(payload, dict):
                    items = [payload] if payload else []
                else:
        	        logging.error(f"Formato inesperado: {type(payload)}")
        	        items = []
            else:
                logging.error(f"Formato inesperado en data: {type(data)}")
                items = []

            if not items:
                logging.debug("Sin más registros, fin de paginación")
                break

            todos.extend(items)
            logging.debug(f"Página offset={offset}: {len(items)} registros")
            #if items:
                #logging.debug(f"Ejemplo cliente: {items[0]}")

            if len(items) < limit:
                logging.debug("Última página detectada")
                break
            offset += limit
            
        logging.debug(f"Total clientes acumulados: {len(todos)}")
        return todos
    except Exception:
        logging.error("Error durante la paginación / parseo JSON", exc_info=True)
        return []

# SOAP a Flowdat via curl
def enviar_estado_flowdat(idgestion, estado):
    usuario = os.getenv("FLOWDAT_USER")
    password = os.getenv("FLOWDAT_PASS")
    tenencia = os.getenv("FLOWDAT_TENENCIA")
    url = os.getenv("FLOWDAT_ENDPOINT")
    if estado == "activo":
        metodo = "activeCmcliente" 
    elif estado == "suspended": 
        metodo = "suspendCmcliente"    
    else:
        raise ValueError(f"Estado inválido: {estado}")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cm="http://138.219.60.2/api/v_2_0_3/cmclienteSoap">
  <soapenv:Header/>
  <soapenv:Body>
   <cm:{metodo}>
    <cm:cli>
        <cm:idgestion>{idgestion}</cm:idgestion>      
        <cm:tenencia>{tenencia}</cm:tenencia>
    </cm:cli>    
  </cm:{metodo}>
 </soapenv:Body>
</soapenv:Envelope>"""

# Registrar el XML completo en el log soap.log 
    soap_logger.info(f"Enviando SOAP a Flowdat ({metodo}) para ID {idgestion}:\n{xml}")

    try:
        result = subprocess.run([
            "curl", 
            "-u", f"{usuario}:{password}",
            "-H", "Content-Type: text/xml;charset=utf-8",
            "-H", f"SOAPAction: {metodo}", 
            "-d", xml,
            url
             ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise RuntimeError(f"curl error: {result.stderr.strip()}")
        if "Fault" in result.stdout:
            raise RuntimeError(f"SOAP Fault: {result.stdout.strip()}")
        print(f"[OK] Estado actualizado para {idgestion}: {estado}")
        return result.stdout.strip()
    except Exception as e:
            raise RuntimeError(f"Error al enviar SOAP con curl: {e}")

# Equivalencia de estados
estado_map = {"enabled": "activo", "blocked": "suspended"}

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
                clientes_logger.info(f"Cambio de estado para cliente {code}: {row[0]} → {estado_nuevo}")
                logger.info(f"Estado modificado para {code}: {row[0]} → {estado_nuevo}")
                c.execute("UPDATE estados_previos SET status = ? WHERE code = ?", (estado_nuevo, code))
                logger.info(f"Estado modificado para {code}: {row[0]} → {estado_nuevo}")
                c.execute("UPDATE estados_previos SET status = ? WHERE code = ?", (estado_nuevo, code))
            except Exception as e:
                logger.error(f"Error SOAP para {code}: {e}")

    conn.commit()
except Exception as e:
    logger.error(f"Error general: {e}")
finally:
    conn.close()
