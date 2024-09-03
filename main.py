from flask import Flask, render_template, redirect, request, flash
import mysql.connector
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BARBEARIA'

logado = False

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="RodrigoMYSQL123",
        database="bd_barbearia"
    )

@app.route('/')
def home():
    global logado
    logado = False
    return render_template('login.html')

@app.route('/adm')
def adm():
    if logado:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("cadastro.html", usuarios=usuarios)
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    # Verifica se o usuário é o administrador
    if nome == 'adm' and senha == '000':
        logado = True
        return redirect('/adm')

    # Verifica o usuário no banco de dados MySQL
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE nome=%s AND senha=%s", (nome, senha))
    usuario = cursor.fetchone()
    cursor.close()
    db.close()

    # Se o usuário existir no banco de dados
    if usuario:
        logado = True
        return render_template("home.html")
    else:
        flash('USUÁRIO INVÁLIDO')
        return redirect("/")

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE nome=%s", (nome,))
    usuario = cursor.fetchone()

    if usuario:
        flash('Usuário já cadastrado.')
        cursor.close()
        db.close()
        return redirect('/adm')

    cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (%s, %s)", (nome, senha))
    db.commit()
    cursor.close()
    db.close()

    flash('Usuário cadastrado com sucesso!')
    return redirect('/adm')

@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    global logado
    logado = True
    usuario = request.form.get('usuarioPexcluir')
    usuarioDict = ast.literal_eval(usuario)
    nome = usuarioDict['nome']

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM usuarios WHERE nome=%s", (nome,))
    db.commit()
    cursor.close()
    db.close()

    flash(F'{nome} EXCLUIDO')
    return redirect('/adm')

if __name__ == "__main__":
    app.run(debug=True)
