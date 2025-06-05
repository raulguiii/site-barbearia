from flask import Flask, render_template, redirect, request, flash, jsonify, session
import mysql.connector
import ast
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BARBEARIA'
app.config['SESSION_TYPE'] = 'filesystem'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="RodrigoMYSQL123",
        database="bd_barbearia"
    )

@app.route('/')
def home():
    usuario_logado = session.get('usuario_logado', None)
    return render_template('home.html', usuario_logado=usuario_logado)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        # Verificar se é o ADM
        if nome == 'adm' and senha == '000':
            session['usuario_logado'] = {
                'nome': 'Administrador',
                'cargo': 'ADM',
                'id': None,
                'salario': None,
                'tempo_de_casa': None,
                'horario_trabalho': None,
                'chave_pix': None
            }
            return redirect('/adm')

        # Verificar barbeiro no banco de dados
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, senha, cargo, salario, tempo_de_casa, horario_trabalho, chave_pix FROM usuarios WHERE nome=%s AND senha=%s", (nome, senha))
        usuario = cursor.fetchone()
        cursor.close()
        db.close()

        if usuario:
            session['usuario_logado'] = {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'cargo': usuario['cargo'],
                'salario': usuario['salario'],
                'tempo_de_casa': usuario['tempo_de_casa'],
                'horario_trabalho': usuario['horario_trabalho'],
                'chave_pix': usuario['chave_pix']
            }
            return redirect('/agendamentos')
        else:
            flash('USUÁRIO INVÁLIDO')
            return redirect('/')
    usuario_logado = session.get('usuario_logado', None)
    return render_template('login.html', usuario_logado=usuario_logado)

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Você saiu com sucesso!')
    return redirect('/')

@app.route('/adm')
def adm():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    usuario_logado = session.get('usuario_logado', None)
    return render_template('cadastro.html', usuarios=usuarios, usuario_logado=usuario_logado)

@app.route('/agendamentos')
def listar_agendamentos():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'Barbeiro':
        flash('Acesso restrito aos barbeiros.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agendamentos ORDER BY data1 ASC, horario ASC")
    agendamentos = cursor.fetchall()
    cursor.close()
    db.close()

    for ag in agendamentos:
        if isinstance(ag['data1'], str):
            ag['data1'] = datetime.strptime(ag['data1'], '%Y-%m-%d').date()

    usuario_logado = session.get('usuario_logado', None)
    return render_template('agendamentos.html', agendamentos=agendamentos, usuario_logado=usuario_logado)

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
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

    cursor.execute("INSERT INTO usuarios (nome, senha, cargo) VALUES (%s, %s, %s)", (nome, senha, 'Barbeiro'))
    db.commit()
    cursor.close()
    db.close()

    flash('Usuário cadastrado com sucesso!')
    return redirect('/adm')

@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
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
    usuario_logado = session.get('usuario_logado', None)
    return render_template('home.html', usuario_logado=usuario_logado)

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
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'Barbeiro':
        flash('Acesso restrito aos barbeiros.')
        return redirect('/')

    nome_barbeiro = session.get('usuario_logado', {}).get('nome')

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
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'Barbeiro':
        flash('Acesso restrito aos barbeiros.')
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()
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
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    usuario_logado = session.get('usuario_logado', None)
    return render_template('cadastrados.html', usuarios=usuarios, usuario_logado=usuario_logado)

@app.route('/relatorio')
def relatorio():
    if not session.get('usuario_logado'):
        flash('Faça login para acessar esta página.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT servico, COUNT(*) as total
        FROM agendamentos
        GROUP BY servico
        ORDER BY total DESC
    """)
    servico_data = cursor.fetchall()

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

    usuario_logado = session.get('usuario_logado', None)
    return render_template(
        'relatorio.html',
        servico_data=servico_data,
        barbeiro_data=barbeiro_data,
        usuario_logado=usuario_logado
    )

@app.route('/cadastro')
def cadastro():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    usuario_logado = session.get('usuario_logado', None)
    return render_template('cadastro.html', usuario_logado=usuario_logado)

@app.route('/financeiro')
def financeiro():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    usuario_logado = session.get('usuario_logado', None)
    return render_template('financeiro.html', usuarios=usuarios, usuario_logado=usuario_logado)

@app.route('/atualizar_informacoes', methods=['POST'])
def atualizar_informacoes():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
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

UPLOAD_FOLDER = 'Uploads/comprovantes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/pagar/<int:id>', methods=['GET', 'POST'])
def pagar(id):
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
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

            db = get_db_connection()
 Huntsman cursor = db.cursor()
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

    usuario_logado = session.get('usuario_logado', None)
    return render_template('pagar.html', usuario_id=id, usuario_logado=usuario_logado)

@app.route('/estoque')
def estoque():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()
    db.close()

    usuario_logado = session.get('usuario_logado', None)
    return render_template('estoque.html', produtos=produtos, usuario_logado=usuario_logado)

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    nome = request.form.get('nome')
    quantidade = request.form.get('quantidade')
    preco = request.form.get('preco')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (%s, %s, %s)", (nome, quantidade, preco))
    db.commit()
    cursor.close()
    db.close()

    flash('Produto adicionado com sucesso!')
    return redirect('/estoque')

@app.route('/editar_produto', methods=['POST'])
def editar_produto():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
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

    flash('Produto editado com sucesso!')
    return redirect('/estoque')

@app.route('/excluir_produto', methods=['POST'])
def excluir_produto():
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    produto_id = request.form.get('id')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
    db.commit()
    cursor.close()
    db.close()

    flash('Produto excluído com sucesso!')
    return redirect('/estoque')

@app.route('/comprar', methods=['POST'])
def comprar():
    nome = request.form.get('name')
    endereco = request.form.get('address')
    metodo_entrega = request.form.get('delivery-method')
    produto = request.form.get('product')

    if not nome or not endereco or not metodo_entrega or not produto:
        flash('Por favor, preencha todos os campos!')
        return redirect('/')

    try:
        db = get_db_connection()
        cursor = db.cursor()
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
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM vendas_produtos")
        dados_vendas = cursor.fetchall()
        vendas = []
        for venda in dados_vendas:
            data_compra = datetime.strptime(str(venda[5]), "%Y-%m-%d %H:%M:%S")
            data_formatada = data_compra.strftime("%d/%m/%Y às %H:%M:%S")
            nova_venda = list(venda)
            nova_venda[5] = data_formatada
            vendas.append(nova_venda)
    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados do banco: {err}")
        vendas = []
    finally:
        cursor.close()
        db.close()

    usuario_logado = session.get('usuario_logado', None)
    return render_template('vendas.html', vendas=vendas, usuario_logado=usuario_logado)

@app.route('/delete_venda/<int:id>', methods=['POST'])
def delete_venda(id):
    if not session.get('usuario_logado') or session.get('usuario_logado', {}).get('cargo') != 'ADM':
        flash('Acesso restrito ao administrador.')
        return redirect('/')
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
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
