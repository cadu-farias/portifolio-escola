import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort, session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'



def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
  
def registrar_usuario(nome, email, senha):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO users(nome, email, senha) values (?,?,?)', (nome, email, senha))
    con.commit()
    con.close()

def checar_usuario(email, senha):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, senha FROM users WHERE email=? and senha=?', (email, senha))

    resultado = cur.fetchone()
    if resultado:
        return True
    else:
        return False

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_users(email):
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users WHERE email = ?',
    (email,)).fetchone()
    conn.close()
    if users is None:
        abort(404)
    return users

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    if session:
        users = get_users(session['email'])
        return render_template('index.html', posts=posts, users=users)
    else:
        return render_template('index.html', posts=posts)

@app.route('/postagens')
def postagens():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    if session:
        users = get_users(session['email'])
        return render_template('postagens.html', posts=posts, users=users)
    else:
        return render_template('postagens.html', posts=posts)

@app.route('/perfil',methods=('GET', 'POST'))
def perfil():
    if not (session):
        return redirect(url_for('index'))
    else:
        users = get_users(session['email'])
        return render_template('perfil.html', users=users)

@app.route('/cadastrar/', methods=('GET', 'POST'))
def cadastrar():
    if (session):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        senha = request.form['senha']
        email = str(email)
        nome = str(nome)
        senha = str(senha)
        if not email:
            flash('Email não pode ficar em branco!')
        elif not nome:
            flash('Nome não pode ficar em branco!')
        elif not senha:
            flash('Senha não pode ficar em branco!')
        else:
            registrar_usuario(nome, email, senha)
            return redirect(url_for('index'))
    return render_template('cadastrar.html')

@app.route('/login/', methods=('GET', 'POST'))
def login():
    if (session):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        email = str(email)
        senha = str(senha)
        if not email:
            flash('Email não pode ficar em branco!')
        elif not senha:
            flash('Senha não pode ficar em branco!')
        elif(checar_usuario(email,senha)):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            flash('Usuario ou senha incorretos!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if not (session):
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Titulo não pode ficar em branco!')
        elif not content:
            flash('Conteudo não pode ficar em branco!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')
  
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)
    if not (session):
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Titulo não pode ficar em branco!')

        elif not content:
            flash('Conteúdo não pode ficar em branco!')

        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/editarPerfil/', methods=('GET', 'POST'))
def editPerfil():
    users = get_users(session['email'])
    id = users['id']
    if not (session):
        return redirect(url_for('index'))
    elif request.method == 'POST':
        nome = request.form['nome']
        atuacao = request.form['atuacao']
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        telefone = request.form['telefone']
        endereco = f'{rua}, {numero}, {bairro}'
        if not nome:
            flash('Nome não pode ficar em branco!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE users SET nome = ?, atuacao = ?, endereco = ?, telefone = ?'
                         ' WHERE id = ?',
                         (nome, atuacao, endereco, telefone, id))
            conn.commit()
            conn.close()
            return redirect(url_for('perfil'))

    return render_template('editPerfil.html', users = users)


@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    if not (session):
        return redirect(url_for('index'))
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

app.debug=1
app.run(host='0.0.0.0', port=81)
