import sqlite3

conn = sqlite3.connect('clientes.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS clientes')
cursor.execute('DROP TABLE IF EXISTS estados_previos')

cursor.execute('''
CREATE TABLE clientes (
    code TEXT PRIMARY KEY,
    status TEXT
)
''')

cursor.execute('''
CREATE TABLE estados_previos (
    code TEXT PRIMARY KEY,
    status TEXT
)
''')

conn.commit()
conn.close()
print('Base de datos inicializada como nueva instalación.')
