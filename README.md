
# Sincronizador de Estado ISPCube → Flowdat

Este sistema consulta el estado de los clientes en ISPCube, lo compara con el último estado registrado localmente, y en caso de cambios, actualiza Flowdat por SOAP.

## ++ Requisitos
- Debian 12 instalación limpia
- Python 3.11+
- SQLite3
- Acceso a ISPCube vía API
- Acceso a Flowdat vía SOAP
- Servidor syslog opcional

## ++ Instalación

```bash
sudo apt update
sudo apt install python3 python3-venv sqlite3 -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ++ Uso

Inicializar base de datos:

```bash
python3 init_db.py
```

Ejecutar sincronización:

```bash
python3 sync_estado_ispcube.py
```

## ++ Cron cada 10 minutos

Archivo `cronjob.txt`:
```cron
*/10 * * * * /bin/bash -c 'cd /ruta/proyecto && source venv/bin/activate && python3 sync_estado_ispcube.py'
```

Instalar cronjob:

```bash
crontab cronjob.txt
```

## ++ Rotacion de Logs 

Cada 30 dias, se conserva 1 año de Logs

```bash
vim /etc/logrotate.d/sync_estado

/root/apiflowdat/sync_estado.log
/root/apiflowdat/clientes.log
/root/apiflowdat/soap.log {
    monthly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    create 640 root root
    sharedscripts
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}

```

## 📄 Logs

- Local: `sync_estado.log`
- Syslog: servidor x.x.x.x puerto xxxx
