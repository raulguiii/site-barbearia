from flask import Flask, render_template, redirect, request, flash, jsonify
import mysql.connector
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BARBEARIA'

logado = False

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="raulgui123!",
        database="bd_barbearia"
    )

@app.route('/')
def home():
    global logado
    logado = False
    return render_template('home.html')

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

@app.route('/login', methods=['GET', 'POST']) 
def login():
    global logado
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if nome == 'adm' and senha == '000':
            logado = True
            return redirect('/adm')

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE nome=%s AND senha=%s", (nome, senha))
        usuario = cursor.fetchone()
        cursor.close()
        db.close()

        if usuario:
            logado = True
            global nome_barbeiro_logado  
            nome_barbeiro_logado = nome  
            return redirect('/agendamentos')  
        else:
            flash('USUÁRIO INVÁLIDO')
            return redirect("/")
    return render_template('login.html')


@app.route('/agendamentos')
def listar_agendamentos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agendamentos ORDER BY data1 ASC, horario ASC") 
    agendamentos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("agendamentos.html", agendamentos=agendamentos)


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
    usuario = request.form.get('usuarioPexcluir')
    usuarioDict = ast.literal_eval(usuario)
    nome = usuarioDict['nome']

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM usuarios WHERE nome=%s", (nome,))
    db.commit()
    cursor.close()
    db.close()

    flash(f'{nome} EXCLUÍDO com sucesso!')  
    return redirect('/cadastrados') 

@app.route('/home')
def cadastraruser():
    return render_template('home.html')

@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form.get('name')
    telefone = request.form.get('phone')
    servico = request.form.get('service')
    data1 = request.form.get('date')
    horario = request.form.get('time')

    if not nome or not telefone or not servico or not data1 or not horario:
        flash('Por favor, preencha todos os campos!')
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM agendamentos WHERE data1 = %s AND horario = %s",
        (data1, horario)
    )
    agendamento_existente = cursor.fetchone()

    if agendamento_existente:
        flash('Esse horário já está agendado. Por favor, escolha outro horário.')
        cursor.close()
        db.close()
        return redirect('/')

    try:
        cursor.execute(
            "INSERT INTO agendamentos (nome, telefone, servico, data1, horario) VALUES (%s, %s, %s, %s, %s)",
            (nome, telefone, servico, data1, horario)
        )
        db.commit()
        flash('Agendamento realizado com sucesso!')
    except mysql.connector.Error as err:
        print(f"Erro ao inserir no banco de dados: {err}")
        flash(f'Erro ao realizar o agendamento: {err}')
    finally:
        cursor.close()
        db.close()

    return redirect('/')

@app.route('/candidatar/<int:agendamento_id>', methods=['GET'])
def candidatar(agendamento_id):
    global logado
    if not logado:
        return redirect('/')  

    nome_barbeiro = nome_barbeiro_logado  

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE agendamentos SET candidato = 1, barbeiro_nome = %s WHERE id = %s",
        (nome_barbeiro, agendamento_id)
    )
    db.commit()
    cursor.close()
    db.close()

    flash('Você se candidatou com sucesso!')
    return redirect('/agendamentos')

@app.route('/cadastrados')
def usuarios_cadastrados():
    if logado:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("cadastrados.html", usuarios=usuarios)
    else:
        return redirect('/')

@app.route('/relatorio')
def relatorio():
    if not logado:
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    
    cursor.execute("""
        SELECT servico, COUNT(*) as total
        FROM agendamentos
        GROUP BY servico
        ORDER BY total DESC
        LIMIT 1
    """)
    servico_mais_realizado = cursor.fetchone()

   
    cursor.execute("""
        SELECT barbeiro_nome, COUNT(*) as total
        FROM agendamentos
        WHERE candidato = 1
        GROUP BY barbeiro_nome
        ORDER BY total DESC
        LIMIT 1
    """)
    barbeiro_mais_candidatou = cursor.fetchone()

   
    cursor.execute("""
        SELECT servico, data1 AS data, barbeiro_nome
        FROM agendamentos
        WHERE candidato = 1
        ORDER BY data1 DESC, horario DESC
        LIMIT 1
    """)
    ultimo_servico = cursor.fetchone()

    cursor.close()
    db.close()

   
    return render_template('relatorio.html', 
        servico=servico_mais_realizado, 
        barbeiro=barbeiro_mais_candidatou, 
        ultimo_servico=ultimo_servico)



@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/financeiro')
def financeiro():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('financeiro.html', usuarios=usuarios)

@app.route('/atualizar_informacoes', methods=['POST'])
def atualizar_informacoes():
    
    usuario_id = request.form.get('usuario_id')
    salario = request.form.get('salario')
    tempo_de_casa = request.form.get('tempo_de_casa')
    horario_trabalho = request.form.get('horario_trabalho')


    db = get_db_connection()
    cursor = db.cursor()

    
    cursor.execute("""
        UPDATE usuarios
        SET salario = %s, tempo_de_casa = %s, horario_trabalho = %s
        WHERE id = %s
    """, (salario, tempo_de_casa, horario_trabalho, usuario_id))

    
    db.commit()

    
    cursor.close()
    db.close()

   
    flash('Informações atualizadas com sucesso!')
    return redirect('/financeiro')

@app.route('/pagar/<int:id>')
def pagar(id):
    print(f"Pagamento iniciado para o usuário com ID: {id}")

    return f"Página de pagamento para o usuário com ID: {id}"



if __name__ == "__main__":
    app.run(debug=True) 
