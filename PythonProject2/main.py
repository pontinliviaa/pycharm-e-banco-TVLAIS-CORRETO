from fdb import Cursor
from flask import Flask, render_template, redirect, request, flash, url_for
import fdb

app = Flask(__name__)
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
                            VALUES(?,?,?)""",(nome, autor, ano))
        con.commit()
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

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1
                          FROM USUARIO
                          WHERE EMAIL = ?""", (email,))

        if cursor.fetchone():
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('novousuario'))

        cursor.execute("""INSERT INTO USUARIO(NOME, EMAIL, SENHA)
                          VALUES(?,?,?)""",
                       (nome, email, senha))

        con.commit()

        flash('Usuário cadastrado com sucesso.')

    except Exception as e:
        flash(f'Ocorreu um erro -> {e}')
        con.rollback()

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
            cursor.execute("""SELECT ID_USUARIO, NOME, EMAIL, SENHA
                              FROM USUARIO
                              WHERE EMAIL = ? AND SENHA = ?""",
                           (email, senha))

            usuario = cursor.fetchone()

            if usuario:
                flash('Login realizado com sucesso!')
                return redirect(url_for('index'))

            else:
                flash('E-mail ou senha incorretos.')

        except Exception as e:

            flash(f'Ocorreu um erro -> {e}')

        finally:
            cursor.close()

    return render_template('login.html')










if __name__ == '__main__':
    app.run(debug=True)