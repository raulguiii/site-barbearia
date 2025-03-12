from flask import Flask, render_template, redirect, request, flash, jsonify
import mysql.connector
import ast
import os
from werkzeug.utils import secure_filename

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

@app.route('/deletar/<int:agendamento_id>', methods=['GET'])
def deletar_agendamento(agendamento_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Verifica se o agendamento tem um barbeiro candidato
    cursor.execute("SELECT candidato FROM agendamentos WHERE id = %s", (agendamento_id,))
    resultado = cursor.fetchone()

    if resultado and resultado[0] == 1:
        try:
            cursor.execute("DELETE FROM agendamentos WHERE id = %s", (agendamento_id,))
            db.commit()
            flash('Agendamento deletado com sucesso!')
        except mysql.connector.Error as err:
            flash(f'Erro ao deletar o agendamento: {err}')
    else:
        flash('Não é possível excluir um agendamento sem um barbeiro candidato.')

    cursor.close()
    db.close()
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

    # Dados do gráfico de serviços
    cursor.execute("""
        SELECT servico, COUNT(*) as total
        FROM agendamentos
        GROUP BY servico
        ORDER BY total DESC
    """)
    servico_data = cursor.fetchall()

    # Dados do gráfico de barbeiros
    cursor.execute("""
        SELECT barbeiro_nome, COUNT(*) as total
        FROM agendamentos
        WHERE candidato = 1
        GROUP BY barbeiro_nome
        ORDER BY total DESC
    """)
    barbeiro_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        'relatorio.html',
        servico_data=servico_data,
        barbeiro_data=barbeiro_data
    )

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
    chave_pix = request.form.get('chave_pix')  

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET salario = %s, tempo_de_casa = %s, horario_trabalho = %s, chave_pix = %s
        WHERE id = %s
    """, (salario, tempo_de_casa, horario_trabalho, chave_pix, usuario_id))

    db.commit()
    cursor.close()
    db.close()

    flash('Informações atualizadas com sucesso!')
    return redirect('/financeiro')


UPLOAD_FOLDER = 'uploads/comprovantes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/pagar/<int:id>', methods=['GET', 'POST'])
def pagar(id):
    if request.method == 'POST':
        if 'comprovante' not in request.files:
            flash('Nenhum arquivo enviado.')
            return redirect(request.url)

        file = request.files['comprovante']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Atualiza o banco de dados com o status "Pago" e o caminho do comprovante
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET pagamento_realizado = 1, comprovante = %s
                WHERE id = %s
            """, (file_path, id))
            db.commit()
            cursor.close()
            db.close()

            flash('Pagamento registrado com sucesso!')
            return redirect('/financeiro')

    return render_template('pagar.html', usuario_id=id)

@app.route('/estoque')
def estoque():
    if not logado:
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('estoque.html', produtos=produtos)


@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome = request.form.get('nome')
    quantidade = request.form.get('quantidade')
    preco = request.form.get('preco')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (%s, %s, %s)", (nome, quantidade, preco))
    db.commit()
    cursor.close()
    db.close()

    return redirect('/estoque')


@app.route('/editar_produto', methods=['POST'])
def editar_produto():
    produto_id = request.form.get('id')
    nome = request.form.get('nome')
    quantidade = request.form.get('quantidade')
    preco = request.form.get('preco')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE produtos SET nome=%s, quantidade=%s, preco=%s WHERE id=%s", (nome, quantidade, preco, produto_id))
    db.commit()
    cursor.close()
    db.close()

    return redirect('/estoque')


@app.route('/excluir_produto', methods=['POST'])
def excluir_produto():
    produto_id = request.form.get('id')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
    db.commit()
    cursor.close()
    db.close()

    return redirect('/estoque')

@app.route('/comprar', methods=['POST'])
def comprar():
    nome = request.form.get('name')
    endereco = request.form.get('address')
    metodo_entrega = request.form.get('delivery-method')
    produto = request.form.get('product')

    # Verifica se todos os campos foram preenchidos
    if not nome or not endereco or not metodo_entrega or not produto:
        flash('Por favor, preencha todos os campos!')
        return redirect('/')

    try:
        # Conecta ao banco de dados
        db = get_db_connection()
        cursor = db.cursor()
        
        # Insere os dados na tabela vendas_produtos
        cursor.execute(
            "INSERT INTO vendas_produtos (nome, endereco, metodo_entrega, produto) VALUES (%s, %s, %s, %s)",
            (nome, endereco, metodo_entrega, produto)
        )
        db.commit()
        flash('Compra realizada com sucesso!')

    except mysql.connector.Error as err:
        print(f"Erro ao inserir no banco de dados: {err}")
        flash(f'Erro ao realizar a compra: {err}')

    finally:
        cursor.close()
        db.close()

    return redirect('/')

@app.route('/vendas', methods=['GET'])
def vendas():
    # Conectar ao banco de dados
    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Buscar todos os registros de vendas
        cursor.execute("SELECT * FROM vendas_produtos")
        vendas = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados do banco: {err}")
        vendas = []

    finally:
        cursor.close()
        db.close()

    return render_template('vendas.html', vendas=vendas)

@app.route('/delete_venda/<int:id>', methods=['POST'])
def delete_venda(id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Deletar a venda do banco de dados
        cursor.execute("DELETE FROM vendas_produtos WHERE id = %s", (id,))
        db.commit()
        flash('Venda excluída com sucesso!')

    except mysql.connector.Error as err:
        print(f"Erro ao excluir no banco de dados: {err}")
        flash(f'Erro ao excluir a venda: {err}')

    finally:
        cursor.close()
        db.close()

    return redirect('/vendas')



if __name__ == "__main__":
    app.run(debug=True) 
