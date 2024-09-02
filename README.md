1. Instale o MySQL Connector para Python
pip install mysql-connector-python


2. Configure o Banco de Dados MySQL
-- Criação do banco de dados
CREATE DATABASE barbearia_db;

-- Seleciona o banco de dados para uso
USE barbearia_db;

-- Criação da tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);



3. Atualize o Código Flask para Usar MySQL
from flask import Flask, render_template, redirect, request, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BARBEARIA'

# Conectar ao banco de dados
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',         # ou o IP do seu servidor MySQL
            user='seu_usuario',       # substitua pelo seu usuário do MySQL
            password='sua_senha',     # substitua pela sua senha do MySQL
            database='barbearia_db'   # nome do banco de dados criado
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

logado = False

@app.route('/')
def home():
    global logado
    logado = False
    return render_template('login.html')

@app.route('/adm')
def adm():
    if logado:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios')
        usuarios = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template("cadastro.html", usuarios=usuarios)
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE nome = %s AND senha = %s', (nome, senha))
    usuario = cursor.fetchone()
    cursor.close()
    connection.close()

    if nome == 'cabeleireiro' and senha == 'LucasAlberto':
        logado = True
        return redirect('/adm')
    
    if usuario:
        return render_template("home.html")
    
    flash('USUARIO INVALIDO')
    return redirect("/")

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('INSERT INTO usuarios (nome, senha) VALUES (%s, %s)', (nome, senha))
        connection.commit()
    except Error as e:
        flash('Usuário já cadastrado.')
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    return redirect('/adm')

@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    global logado
    logado = True
    usuario = request.form.get('usuarioPexcluir')
    usuarioDict = ast.literal_eval(usuario)
    nome = usuarioDict['nome']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM usuarios WHERE nome = %s', (nome,))
    connection.commit()
    cursor.close()
    connection.close()

    flash(f'{nome} EXCLUIDO')
    return redirect('/adm')

if __name__ == "__main__":
    app.run(debug=True)
