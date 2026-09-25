
from flask import Flask, render_template, redirect, request, flash, url_for, session, send_file
import fdb
import re
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'aqui_chave_turmaA'

host = "localhost"
database = r'C:\Users\Aluno\Downloads\atv-lais-pycharm-main\atv-lais-pycharm-main\pycharm-e-banco-main\pycharm-e-banco-main\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route("/")
def index():

    cursor = con.cursor() #abrindo o cursor
    cursor.execute("""SELECT ID_LIVRO, NOME, AUTOR, ANO_PUB FROM LIVRO
                   ORDER BY NOME""")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)


@app.route('/novo')
def novo():
    if 'id_usuario' not in session:
        flash('Precisar estar logado')
        return redirect(url_for('login'))
    else:
        return render_template('novo.html', titulo='novo livro')
    return render_template('novo.html')


@app.route('/criar', methods = ['POST'])
def criar():
    nome = request.form['nome']
    autor = request.form['autor']
    ano = request.form['ano']
    cursor = con.cursor()
    try:
        cursor.execute("""SELECT 1
                            FROM LIVRO WHERE NOME = ?""", (nome,))
        if cursor.fetchone():
            flash('Erro ao cadastrar o livro.')
            return redirect(url_for('novo'))

        cursor.execute("""INSERT INTO LIVRO(NOME, AUTOR, ANO_PUB)
                            VALUES(?,?,?) RETURNING ID_LIVRO""",(nome, autor, ano))
        id_livro = cursor.fetchone()[0]
        con.commit()

        arquivo = request.files['imagem']
        arquivo.save(f'uploads/capa{id_livro}.jpg')
        flash('Livro cadastrado com sucesso.')

    except Exception as e:
        flash(f'Ocorreu um erro -> {e}')
        con.rollback()

    finally:
        cursor.close()
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""SELECT ID_LIVRO, NOME, AUTOR, ANO_PUB
            FROM LIVRO WHERE ID_LIVRO = ?""", (id,))
        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado.')
            return redirect(url_for('index'))

        if request.method == 'POST':
            nome = request.form['nome']
            autor = request.form['autor']
            ano = request.form['ano']

            cursor.execute("""UPDATE LIVRO SET NOME = ?, AUTOR = ?, ANO_PUB = ? 
                    WHERE ID_LIVRO = ? """, (nome, autor, ano, id))
            con.commit()
            flash('Livro editado.')
            return redirect(url_for('index'))

        return render_template('editar.html', livro = livro)

    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro ->{e}')
        return redirect(url_for('index'))

    finally:
        cursor.close()


@app.route('/deletar/<int:id>', methods=['post'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("""DELETE FROM LIVRO WHERE ID_LIVRO = ?""", (id,))
        con.commit()
        flash("Livro deletado com sucesso!")
        return redirect(url_for('index'))

    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')
        return redirect(url_for('index'))

    finally:
        cursor.close()

@app.route('/usuarios')
def usuarios():
    cursor = con.cursor()

    cursor.execute("""SELECT ID_USUARIO, NOME, EMAIL, SENHA
                      FROM USUARIO
                      ORDER BY NOME""")

    usuarios = cursor.fetchall()
    cursor.close()

    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/novousuario')
def novousuario():
    return render_template('novousuario.html')

@app.route('/criarusuario', methods=['POST'])
def criarusuario():

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    # Verifica se a senha é forte
    if len(senha) < 8:
        flash('A senha deve ter pelo menos 8 caracteres.')
        return redirect(url_for('novousuario'))

    if not re.search(r'[A-Z]', senha):
        flash('A senha deve ter uma letra maiúscula.')
        return redirect(url_for('novousuario'))

    if not re.search(r'[a-z]', senha):
        flash('A senha deve ter uma letra minúscula.')
        return redirect(url_for('novousuario'))

    if not re.search(r'[0-9]', senha):
        flash('A senha deve ter um número.')
        return redirect(url_for('novousuario'))

    if not re.search(r'[^A-Za-z0-9]', senha):
        flash('A senha deve ter um caractere especial.')
        return redirect(url_for('novousuario'))

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1
                          FROM USUARIO
                          WHERE EMAIL = ?""", (email,))

        if cursor.fetchone():
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('novousuario'))

        # Criptografa a senha
        senha_criptografada = bcrypt.generate_password_hash(senha).decode('utf-8')

        cursor.execute("""INSERT INTO USUARIO
                          (NOME, EMAIL, SENHA, TENTATIVAS, BLOQUEADO)
                          VALUES (?, ?, ?, 0, 0)""",
                       (nome, email, senha_criptografada))

        con.commit()

        flash('Usuário cadastrado com sucesso.')

    except Exception as e:
        con.rollback()
        flash(f'Ocorreu um erro -> {e}')

    finally:
        cursor.close()

    return redirect(url_for('usuarios'))


@app.route('/editarusuario/<int:id>', methods=['GET', 'POST'])
def editarusuario(id):

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT ID_USUARIO, NOME, EMAIL, SENHA
                          FROM USUARIO
                          WHERE ID_USUARIO = ?""", (id,))

        usuario = cursor.fetchone()

        if not usuario:
            flash('Usuário não encontrado.')
            return redirect(url_for('usuarios'))

        if request.method == 'POST':

            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            cursor.execute("""UPDATE USUARIO
                              SET NOME = ?, EMAIL = ?, SENHA = ?
                              WHERE ID_USUARIO = ?""",
                           (nome, email, senha, id))

            con.commit()

            flash('Usuário editado.')

            return redirect(url_for('usuarios'))

        return render_template('editarusuario.html', usuario=usuario)

    except Exception as e:

        con.rollback()

        flash(f'Ocorreu um erro -> {e}')

        return redirect(url_for('usuarios'))

    finally:
        cursor.close()


@app.route('/deletarusuario/<int:id>', methods=['POST'])
def deletarusuario(id):

    cursor = con.cursor()

    try:
        cursor.execute("""DELETE FROM USUARIO
                          WHERE ID_USUARIO = ?""", (id,))

        con.commit()

        flash('Usuário deletado com sucesso!')

        return redirect(url_for('usuarios'))

    except Exception as e:

        con.rollback()

        flash(f'Ocorreu um erro -> {e}')

        return redirect(url_for('usuarios'))

    finally:
        cursor.close()


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()

        try:
            cursor.execute("""SELECT ID_USUARIO, NOME, EMAIL, SENHA,
                                     TENTATIVAS, BLOQUEADO
                              FROM USUARIO
                              WHERE EMAIL = ?""",
                           (email,))

            usuario = cursor.fetchone()

            if not usuario:
                flash('E-mail ou senha incorretos.')
                return render_template('login.html')

            id_usuario = usuario[0]
            nome = usuario[1]
            senha_banco = usuario[3]
            tentativas = usuario[4]
            bloqueado = usuario[5]

            # verifica se o usuário está bloqueado
            if bloqueado == 1:
                flash('Usuário bloqueado.')
                return render_template('login.html')

            # verifica a senha
            if bcrypt.check_password_hash(senha_banco, senha):

                # zera as tentativas quando acertar
                cursor.execute("""UPDATE USUARIO
                                  SET TENTATIVAS = 0
                                  WHERE ID_USUARIO = ?""",
                               (id_usuario,))

                con.commit()

                flash(f'Login realizado com sucesso, {nome}!')

                return redirect(url_for('index'))

            else:

                tentativas = tentativas + 1

                if tentativas >= 3:

                    cursor.execute("""UPDATE USUARIO
                                      SET TENTATIVAS = ?, BLOQUEADO = 1
                                      WHERE ID_USUARIO = ?""",
                                   (tentativas, id_usuario))

                    con.commit()

                    flash('Usuário bloqueado por excesso de tentativas.')

                else:

                    cursor.execute("""UPDATE USUARIO
                                      SET TENTATIVAS = ?
                                      WHERE ID_USUARIO = ?""",
                                   (tentativas, id_usuario))

                    con.commit()

                    flash(f'Senha incorreta. Tentativa {tentativas} de 3.')

        except Exception as e:

            con.rollback()

            flash(f'Ocorreu um erro -> {e}')

        finally:
            cursor.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    flash('logouteado')
    return redirect(url_for('login'))

@app.route('/livros/relatorio', methods=['GET'])
def relatorio():

    cursor = con.cursor()

    cursor.execute("""
        SELECT id_livro, titulo, autor, ano_publicacao
        FROM livros
    """)

    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatório de Livros", ln=True, align='C')

    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)

    for livro in livros:
        pdf.cell(
            200,
            10,
            f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}",
            ln=True
        )

    contador_livros = len(livros)

    pdf.ln(10)  # Espaço antes do contador

    pdf.set_font("Arial", style='B', size=12)

    pdf.cell(
        200,
        10,
        f"Total de livros cadastrados: {contador_livros}",
        ln=True,
        align='C'
    )

    pdf_path = "relatorio_livros.pdf"

    pdf.output(pdf_path)

    return send_file(
        pdf_path,
        as_attachment=True,
        mimetype='application/pdf'
    )












if __name__ == '__main__':
    app.run(debug=True)