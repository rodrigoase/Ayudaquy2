import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL, MySQLdb
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

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
#APP.config['MYSQL_CURSORCLASS'] = 'DictCursor'
MYSQL = MySQL(APP)

#Configuracion
APP.secret_key = 'mysecretkey'
APP.config['UPLOAD_FOLDER'] = './static/img'

bcrypt = Bcrypt(APP)

@APP.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@APP.route('/')
def index():
    return render_template('index.html')

@APP.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = MYSQL.connection.cursor()
        sql = 'SELECT * FROM tbusers WHERE email = "' + email + '"'
        cur.execute(sql)
        data = cur.fetchone()
        cur.close()
        if data is None:
            flash('Usuario o contraseña inválidos')
            return redirect(url_for('login'))
        else:
            if bcrypt.check_password_hash(data[5],password.decode('utf-8')):
                if data[7]=='ACTIVO':
                    session['fullname'] = data[1]
                    session['email'] = data[4]
                    session['rol'] = data[6]
                    return redirect(url_for('index'))
                else:
                    flash('El usuario está inactivo')
                    return redirect(url_for('login'))
            else:
                flash('Usuario o contraseña inválidos')
                return redirect(url_for('login'))

@APP.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login')) 

@APP.route('/registro', methods=["GET","POST"])
def registro():
    if request.method == "GET":
        return render_template('registro.html')
    else:
        fullname = request.form['fullname']
        apepaterno = request.form['apepaterno']
        apematerno = request.form['apematerno']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.generate_password_hash(password,10).decode('utf-8')

        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBUSERS (fullname,apepaterno,apematerno,email,password,rol,estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (fullname,apepaterno,apematerno,email,hash_password,'USER','ACTIVO'))
        MYSQL.connection.commit()
        session['fullname'] = fullname
        session['email'] = email

        return redirect(url_for('login'))
        
@APP.route('/admin')
def admin():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBUSERS')
    data = cur.fetchall()
    return render_template('administrador.html', usuarios = data) #se le pasan los datos al template

@APP.route('/crearUsuario', methods=['POST'])
def addUser():
    if request.method == 'POST':
        fullname = request.form['fullname']
        apepaterno = request.form['apepaterno']
        apematerno = request.form['apematerno']
        email = request.form['email']
        password = 'admin'
        estado = request.form['estado']
        hash_password = bcrypt.generate_password_hash(password,10).decode('utf-8')

        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBUSERS (fullname,apepaterno,apematerno,email,password,rol,estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (fullname,apepaterno,apematerno,email,hash_password,'ADMIN',estado))
        MYSQL.connection.commit()

        flash('Usuario creado satisfactoriamente')
        return redirect(url_for('admin'))

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
        apepaterno = request.form['apepaterno']
        apematerno = request.form['apematerno']
        email = request.form['email']
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBUSERS SET FULLNAME = %s, APEPATERNO = %s, APEMATERNO = %s, EMAIL = %s, ESTADO = %s  WHERE ID = %s', [fullname,apepaterno,apematerno,email,estado,id])
        MYSQL.connection.commit()
        flash('Usuario actualizado satisfactoriamente')
        return redirect(url_for('admin'))

@APP.route('/eliminarUsuario/<id>')
def deleteUser(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBUSERS WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Usuario eliminado satisfactoriamente')
    return redirect(url_for('admin'))

@APP.route('/mapa')
def gmap():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ESTADO=%s', ['ACTIVO'])
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
        while True:
            name = request.form['name']
            description = request.form['description']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            image = request.files['image'].filename
            estado = request.form['estado']
            cur = MYSQL.connection.cursor()
            cur.execute('INSERT INTO TBPLACES (name,description,latitude,longitude,image,estado) VALUES (%s, %s, %s, %s, %s, %s)',
            (name,description,latitude,longitude,image,estado))
            MYSQL.connection.commit()
            f = request.files['image']
            filename = secure_filename(f.filename)
            f.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            flash('Ubicación creada satisfactoriamente')
            return redirect(url_for('places'))
        try:
            name = str(name)
            description = str(description)
            latitude = float(latitude)
            longitude = float(longitude)
            estado = str(estado)

            return name, description,latitude,longitude,estado
        except ValueError:
            print ("ATENCIÓN: Debe llenar todos los campos.")

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
        image = request.files['image'].filename
        estado = request.form['estado']
        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBPLACES SET NAME = %s, DESCRIPTION = %s, LATITUDE = %s, LONGITUDE = %s, IMAGE = %s, ESTADO = %s  WHERE ID = %s', [name,description,latitude,longitude,image,estado,id])
        MYSQL.connection.commit()
        f = request.files['image']
        filename = secure_filename(f.filename)
        f.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
        flash('Ubicación actualizada satisfactoriamente')
        return redirect(url_for('places'))


@APP.route('/eliminarUbicacion/<id>')
def deletePlace(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBPLACES WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Ubicación eliminada satisfactoriamente')
    return redirect(url_for('places'))

@APP.route('/perfilUbicacion/<id>')
def perfilUbicacion(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ID = %s', [id])
    data = cur.fetchall()
    return render_template('perfilTemplate.html', ubicacion = data[0])

if __name__ == '__main__':
    APP.run(
        debug = True,
    )
