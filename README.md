
# Sincronizador de Estado ISPCube → Flowdat

Este sistema consulta el estado de los clientes en ISPCube, lo compara con el último estado registrado localmente, y en caso de cambios, actualiza Flowdat por SOAP.

## 🧱 Requisitos

- Python 3.11+
- SQLite3
- Acceso a ISPCube vía API
- Acceso a Flowdat vía SOAP
- Servidor syslog opcional

## 🔧 Instalación

```bash
sudo apt update
sudo apt install python3 python3-venv sqlite3 -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Uso

Inicializar base de datos:

```bash
python3 init_db.py
```

Ejecutar sincronización:

```bash
python3 sync_estado_ispcube.py
```

## 🗓️ Cron cada 30 minutos

Archivo `cronjob.txt`:
```cron
*/30 * * * * /bin/bash -c 'cd /ruta/proyecto && source venv/bin/activate && python3 sync_estado_ispcube.py'
```

Instalar cronjob:

```bash
crontab cronjob.txt
```

## 📄 Logs

- Local: `sync_estado.log`
- Syslog: servidor 10.0.0.182 puerto 1024
