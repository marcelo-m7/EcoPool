import sqlite3
conn = sqlite3.connect('ecopool.db')
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute('''
INSERT INTO registro_variaveis (date, setpoint, diferencial, cenario, duration)
VALUES (datetime('now'), 300, 30, 20, 1000);

''')

conn.commit()
conn.close()
#
#     # Resto do código...
#
#
# conn = get_db()
# cursor = conn.cursor()
#
# cursor.execute('SELECT user_id, username, password FROM users WHERE username = ? AND password = ?',
#                (username, password))
# result = cursor.fetchone()