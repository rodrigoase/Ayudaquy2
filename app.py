from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

APP = Flask(
    __name__,
    static_folder='static',
    static_url_path='/',
)

#Conexión a MySQL
APP.config['MYSQL_HOST'] = 'localhost'
APP.config['MYSQL_USER'] = 'root'
# APP.config['MYSQL_PASSWORD'] = 'password'
APP.config['MYSQL_DB'] = 'ayudaquydb'
MYSQL = MySQL(APP)

#Configuracion
APP.secret_key = 'mysecretkey'

def getLogin(user, password):
    if (user == 'dventura' and password == 'Diego123.'):
        return True
    else:
        return False

def registrarUsuario(user, mail, password):
    print(f'Regitrando al {user} con correo {mail} y clave {password}')
    return True

@APP.route('/')
def index():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBUSERS')
    data = cur.fetchall()
    return render_template('administrador.html', usuarios = data) #se le pasan los datos al template

@APP.route('/crearUsuario', methods=['POST'])
def addUser():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBUSERS (fullname,email,estado) VALUES (%s, %s, %s)',
        (fullname,email,estado))
        MYSQL.connection.commit()
        flash('Usuario creado satisfactoriamente')
        return redirect(url_for('index'))

@APP.route('/editarUsuario/<id>')
def getUser(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBUSERS WHERE ID = %s', (id))
    data = cur.fetchall()
    return render_template('editarUsuario.html', usuario = data[0])

@APP.route('/actualizarUsuario/<id>', methods = ['POST'])
def updateUser(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBUSERS SET FULLNAME = %s, EMAIL = %s, ESTADO = %s  WHERE ID = %s', (fullname,email,estado,id))
        MYSQL.connection.commit()
        flash('Usuario actualizado satisfactoriamente')
        return redirect(url_for('index'))

@APP.route('/eliminarUsuario/<id>')
def deleteUser(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBUSERS WHERE ID = %s', (id))
    MYSQL.connection.commit()
    flash('Usuario eliminado satisfactoriamente')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/ingreso_tienda', methods=['POST'])
def ingreso_tienda():
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']

        if getLogin(usr,pwd):
            return render_template('index.html')
        else:
            return render_template('login.html', mensaje = 'Error, acceso denegado')

@app.route('/registro_usr', methods=['POST'])
def registro_usr():
    if request.method == 'POST':
        usr = request.form['username']
        mail = request.form['mail']
        pwd = request.form['password']

        if(registrarUsuario(usr,mail,pwd)):
            return render_template('login.html', mensaje='Registro correcto')
        else:
            return render_template('registro.html', mensaje='Error durante registro')

if __name__ == '__main__':
    APP.run(
        debug = True,
    )