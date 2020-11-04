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
    cur.execute('SELECT * FROM TBUSERS WHERE ID = %s', [id])
    data = cur.fetchall()
    return render_template('editarUsuario.html', usuario = data[0])

@APP.route('/actualizarUsuario/<id>', methods = ['POST'])
def updateUser(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBUSERS SET FULLNAME = %s, EMAIL = %s, ESTADO = %s  WHERE ID = %s', [fullname,email,estado,id])
        MYSQL.connection.commit()
        flash('Usuario actualizado satisfactoriamente')
        return redirect(url_for('index'))

@APP.route('/eliminarUsuario/<id>')
def deleteUser(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBUSERS WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Usuario eliminado satisfactoriamente')
    return redirect(url_for('index'))

@APP.route('/mapa')
def gmap():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES')
    data = cur.fetchall()
    #print(data)
    return render_template('map.html', ubicaciones = data)

@APP.route('/ubicaciones')
def places():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES')
    data = cur.fetchall()
    return render_template('ubicaciones.html', ubicaciones = data)

@APP.route('/crearUbicacion', methods=['POST'])
def addPlace():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBPLACES (name,description,latitude,longitude,estado) VALUES (%s, %s, %s, %s, %s)',
        (name,description,latitude,longitude,estado))
        MYSQL.connection.commit()
        flash('Ubicación creada satisfactoriamente')
        return redirect(url_for('places'))

@APP.route('/editarUbicacion/<id>')
def getPlace(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ID = %s', [id])
    data = cur.fetchall()
    return render_template('editarUbicacion.html', ubicacion = data[0])

@APP.route('/actualizarUbicacion/<id>', methods = ['POST'])
def updatePlace(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBPLACES SET NAME = %s, DESCRIPTION = %s, LATITUDE = %s, LONGITUDE = %s, ESTADO = %s  WHERE ID = %s', [name,description,latitude,longitude,estado,id])
        MYSQL.connection.commit()
        flash('Ubicación actualizada satisfactoriamente')
        return redirect(url_for('places'))


@APP.route('/eliminarUbicacion/<id>')
def deletePlace(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBPLACES WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Ubicación eliminada satisfactoriamente')
    return redirect(url_for('places'))

if __name__ == '__main__':
    APP.run(
        debug = True,
    )

