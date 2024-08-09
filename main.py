

from flask import Flask, render_template, redirect, request, flash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BARBEARIA'

logado = False

@app.route('/')
def home():
    global logado
    logado = False
    return render_template('login.html')

@app.route('/adm')
def adm():
    if logado == True:
        return render_template("cadastro.html")
    if logado == False:
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
        cont = 0
        for usuario in usuarios:
            cont += 1

            if nome == 'adm' and senha == '000':
                logado = True
                return redirect('/adm')

            if usuario['nome'] == nome and usuario['senha'] == senha:
                return render_template("home.html")
            
            if cont >= len(usuarios):
                flash('USUARIO INVALIDO')
                return redirect("/")

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    # Carregar usuários existentes
    with open('usuarios.json', 'r') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

    # Verificar se o nome de usuário já existe
    for usuario in usuarios:
        if usuario['nome'] == nome:
            flash('Usuário já cadastrado.')
            return redirect('/adm')

    # Adicionar o novo usuário se não houver duplicata
    novo_usuario = {
        "nome": nome,
        "senha": senha
    }
    usuarios.append(novo_usuario)

    # Salvar a lista atualizada de usuários
    with open('usuarios.json', 'w') as gravarTemp:
        json.dump(usuarios, gravarTemp, indent=4)

    return redirect('/adm')






if __name__ in "__main__":
    app.run(debug=True)    
