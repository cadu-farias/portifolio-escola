import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (email, nome, senha) VALUES (?, ?, ?)",
            ('email@gmail.com', 'Nome sobrenome', 'senha123')
            )

connection.commit()
connection.close()