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

#CORS(APP)

#Conexión a MySQL
APP.config['MYSQL_HOST'] = 'localhost'
APP.config['MYSQL_USER'] = 'root'
#APP.config['MYSQL_PASSWORD'] = 'root'
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
    posts = get_posts()
    comments = get_comments()
    return render_template('index.html', posts= posts, comments=comments)

@APP.route('/quienesSomos')
def info():
    return render_template('quienesSomos.html')

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
                    session['idorg'] = data[8]
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

@APP.route('/registroOrganizacion', methods=["GET","POST"])
def registroOrg():
    if request.method == "GET":
        return render_template('registroOrg.html')
    else:
        rsocial = request.form['rsocial']
        ruc = request.form['ruc']
        nrotelefono = request.form['nrotelefono']
        email = request.form['email']
        djurada = request.files['djurada']
        password = request.form['ruc'].encode('utf-8')
        hash_password = bcrypt.generate_password_hash(password,10).decode('utf-8')

        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBORGANIZACION (rsocial,ruc,nrotelefono,email,djurada,estado) VALUES (%s, %s, %s, %s, %s, %s)',
        (rsocial,ruc,nrotelefono,email,djurada,'INACTIVO'))
        MYSQL.connection.commit()

        cur = MYSQL.connection.cursor()
        cur.execute('SELECT id FROM TBORGANIZACION WHERE ruc = %s', [ruc])
        idorg = cur.fetchall()
        cur.execute('INSERT INTO TBUSERS (fullname,email,password,rol,idorg,estado) VALUES (%s, %s, %s, %s, %s, %s)',
        (rsocial,email,hash_password,'ORG',idorg,'INACTIVO'))
        MYSQL.connection.commit()
        #session['fullname'] = fullname
        #session['email'] = email

        return redirect(url_for('mensaje'))

@APP.route('/mensaje', methods=["GET"])
def mensaje():
    if request.method == "GET":
        return render_template('mensaje.html')

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

#Gestion de ubicaciones

@APP.route('/ubicaciones')
def places():
    idorg= session['idorg']
    cur = MYSQL.connection.cursor()
    if idorg == 0:
        cur.execute('SELECT * FROM TBPLACES')
    else:
        cur.execute('SELECT * FROM TBPLACES WHERE IDORG = %s',[idorg])
    data = cur.fetchall()
    return render_template('ubicaciones.html', ubicaciones = data)

@APP.route('/crearUbicacion', methods=['POST'])
def addPlace():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        image = request.files['image'].filename
        estado = request.form['estado']
        idorg = session['idorg']

        cur = MYSQL.connection.cursor()
        if len(image) != 0:
            f = request.files['image']
            filename = secure_filename(f.filename)
            f.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            cur.execute('INSERT INTO TBPLACES (name,description,latitude,longitude,image,estado,idorg) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (name,description,latitude,longitude,image,estado,idorg))
        else:
            cur.execute('INSERT INTO TBPLACES (name,description,latitude,longitude,estado,idorg) VALUES (%s, %s, %s, %s, %s, %s)',
            (name,description,latitude,longitude,estado,idorg))
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
        image = request.files['image'].filename
        estado = request.form['estado']
        idorg = session['idorg']

        cur = MYSQL.connection.cursor()
        if len(image) != 0:
            f = request.files['image']
            filename = secure_filename(f.filename)
            f.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            cur.execute('UPDATE TBPLACES SET NAME = %s, DESCRIPTION = %s, LATITUDE = %s, LONGITUDE = %s, IMAGE = %s, ESTADO = %s, IDORG = %s  WHERE ID = %s', [name,description,latitude,longitude,image,estado,idorg,id])
        else:
            cur.execute('UPDATE TBPLACES SET NAME = %s, DESCRIPTION = %s, LATITUDE = %s, LONGITUDE = %s, ESTADO = %s, IDORG = %s  WHERE ID = %s', [name,description,latitude,longitude,estado,idorg,id])
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

@APP.route('/perfilUbicacion/<id>')
def perfilUbicacion(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ID = %s', [id])
    data = cur.fetchall()
    cur.execute('SELECT A.ID,A.ELEMENTO,B.nomunidad,A.cantmeta,A.cantactual FROM TBREQS A, TBUNIMEDIDA B WHERE IDUBICACION = %s AND A.idunidad = B.id', [id])
    reqs = cur.fetchall()
    progreso = round(calcularProgreso(id)*100)
    print(progreso)
    return render_template('perfilTemplate.html', ubicacion = data[0], reqs = reqs, progreso = progreso)

def calcularProgreso(id):
    cur = MYSQL.connection.cursor()
    cur.execute('select SUM(cantactual)/sum(cantmeta) from tbreqs where idubicacion=%s group by idunidad',[id])
    progxunidad = cur.fetchall()
    cur.execute('select COUNT(id) from tbreqs where idubicacion=%s group by idunidad',[id])
    cantxunidad = cur.fetchall()
    cur.execute('select COUNT(id) from tbreqs where idubicacion=%s',[id])
    canttotal = cur.fetchall()
    progtotal = 0

    for i in range(len(cantxunidad)):
        progtotal = progtotal + float(progxunidad[i][0])*(cantxunidad[i][0]/canttotal[0][0])

    return progtotal

#Gestion de necesidades
@APP.route('/necesidades/<id>')
def getReq(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ID = %s', [id])
    data = cur.fetchall()
    cur.execute('SELECT * FROM TBUNIMEDIDA')
    unidades = cur.fetchall()
    cur.execute('SELECT A.ID,A.ELEMENTO,B.nomunidad,A.cantmeta,A.cantactual FROM TBREQS A, TBUNIMEDIDA B WHERE IDUBICACION = %s AND A.idunidad = B.id', [id])
    reqs = cur.fetchall()
    return render_template('necesidades.html', ubicacion = data[0], unidades = unidades, reqs = reqs)

@APP.route('/agregarNecesidad/<id>', methods=['POST'])
def addReq(id):
    if request.method == 'POST':
        elemento = request.form['elemento']
        cantmeta = request.form['cantmeta']
        idunidad = request.form['idunidad']
        idubicacion = id

        cur = MYSQL.connection.cursor()
        cur.execute('INSERT INTO TBREQS (elemento,cantmeta,idunidad,idubicacion) VALUES (%s, %s, %s, %s)',
        (elemento,cantmeta,idunidad,idubicacion))
        MYSQL.connection.commit()

        flash('Necesidad agregada satisfactoriamente')
        return redirect(url_for('getReq',id = idubicacion))

@APP.route('/<idubica>/editarNecesidad/<id>')
def getNecesidad(idubica,id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBPLACES WHERE ID = %s', [idubica])
    data = cur.fetchall()
    cur.execute('SELECT * FROM TBUNIMEDIDA')
    unidades = cur.fetchall()
    cur.execute('SELECT A.ID,A.ELEMENTO,A.IDUNIDAD,A.cantmeta,A.cantactual,B.nomunidad FROM TBREQS A,TBUNIMEDIDA B WHERE A.IDUBICACION = %s AND A.id= %s AND A.idunidad = B.id', [idubica,id])
    reqs = cur.fetchall()
    return render_template('editarNecesidad.html', ubicacion = data[0], unidades = unidades, reqs = reqs[0])

@APP.route('/<idubica>/actualizarNecesidad/<id>', methods = ['POST'])
def updateReq(idubica,id):
    if request.method == 'POST':
        elemento = request.form['elemento']
        cantmeta = request.form['cantmeta']
        cantactual = request.form['cantactual']
        idunidad = request.form['idunidad']
        idubicacion = idubica

        cur = MYSQL.connection.cursor()
        cur.execute('UPDATE TBREQS SET ELEMENTO = %s, CANTMETA = %s, CANTACTUAL = %s, IDUNIDAD = %s, IDUBICACION = %s  WHERE ID = %s', [elemento,cantmeta,cantactual,idunidad,idubicacion,id])
        MYSQL.connection.commit()
        flash('Necesidad actualizada satisfactoriamente')
        return redirect(url_for('getReq',id = idubicacion))

@APP.route('/<idubica>/eliminarNecesidad/<id>')
def deleteReq(idubica,id):
    idubicacion = idubica
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBREQS WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Necesidad eliminada satisfactoriamente')
    return redirect(url_for('getReq',id = idubicacion))

#Gestión de organizaciones

@APP.route('/organizaciones')
def orgs():
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBORGANIZACION')
    data = cur.fetchall()
    return render_template('organizaciones.html', organizaciones = data)

# @APP.route('/crearOrganizacion', methods=['POST'])
# def addOrg():

#     if request.method == 'POST':
#         rsocial = request.form['rsocial']
#         ruc = request.form['ruc']
#         nrotelefono = request.form['nrotelefono']
#         email = request.form['email']
#         djurada = request.files['djurada']
#         description = request.form['description']
#         estado = request.form['estado']

#         cur = MYSQL.connection.cursor()
#         cur.execute('INSERT INTO TBORGANIZACION (rsocial,ruc,nrotelefono,email,djurada,description,estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
#         (rsocial,ruc,nrotelefono,email,djurada,description,estado))

#         MYSQL.connection.commit()
#         flash('Organización creada satisfactoriamente')
#         return redirect(url_for('orgs'))

@APP.route('/editarOrganizacion/<id>')
def getOrg(id):
    cur = MYSQL.connection.cursor()
    cur.execute('SELECT * FROM TBORGANIZACION WHERE ID = %s', [id])
    data = cur.fetchall()
    return render_template('editarOrganizacion.html', organizacion = data[0])

@APP.route('/actualizarOrganizacion/<id>', methods = ['POST'])
def updateOrg(id):
    if request.method == 'POST':
        rsocial = request.form['rsocial']
        ruc = request.form['ruc']
        nrotelefono = request.form['nrotelefono']
        email = request.form['email']
        djurada = request.files['djurada']
        ndjurada = request.files['djurada'].filename
        description = request.form['description']
        estado = request.form['estado']

        cur = MYSQL.connection.cursor()
        if len(ndjurada) != 0:
            cur.execute('UPDATE TBORGANIZACION SET RSOCIAL = %s, RUC = %s, NROTELEFONO = %s, EMAIL = %s, DJURADA = %s, DESCRIPTION = %s, ESTADO = %s  WHERE ID = %s', [rsocial,ruc,nrotelefono,email,djurada,description,estado,id])
        else:
            cur.execute('UPDATE TBORGANIZACION SET RSOCIAL = %s, RUC = %s, NROTELEFONO = %s, EMAIL = %s, DESCRIPTION = %s, ESTADO = %s  WHERE ID = %s', [rsocial,ruc,nrotelefono,email,description,estado,id])
        MYSQL.connection.commit()
        flash('Organización actualizada satisfactoriamente')
        return redirect(url_for('orgs'))

@APP.route('/eliminarOrganizacion/<id>')
def deleteOrg(id):
    cur = MYSQL.connection.cursor()
    cur.execute('DELETE FROM TBORGANIZACION WHERE ID = %s', [id])
    MYSQL.connection.commit()
    flash('Organización eliminada satisfactoriamente')
    return redirect(url_for('orgs'))

#Servicios REST de publicaciones y comentarios
@APP.route('/post', methods=['POST'])
def posts():
    if request.method == 'POST':
        print('paso')
        name = request.form.get('name')
        post = request.form.get('post')
        if len(name) > 0 and len(post) > 0:
            create_post(str(name), str(post))
            flash('Se acaba de publicar tu mensaje!', 'success')
        else:
            flash('Post no se pudo publicar', 'danger')
    return redirect(url_for('index'))

@APP.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    posts = get_posts()
    if request.method == 'POST':
        delete_post(id)
        flash('Publicación eliminada', 'success')
        return redirect(url_for('index'))

@APP.route('/comments', methods=['POST'])
def comments():
    if request.method == 'POST':
        id_post = request.form.get('id_post')
        name = request.form.get('name')
        content = request.form.get('content')
        print(id_post, name, content)
        create_comments(id_post,name,content)
        return redirect(url_for('index'))

#Funciones de las publicaciones y comentarios
def create_post(name, content):
    cur = MYSQL.connection.cursor()
    cur.execute('insert into posts (name, content) values (%s, %s)', (name, content))
    MYSQL.connection.commit()

def get_posts():
    cur = MYSQL.connection.cursor()
    cur.execute('select * from posts order by FechaCreacion')
    posts = cur.fetchall()
    return posts

def delete_post(id):
    cur = MYSQL.connection.cursor()
    cur.execute('Delete from posts where id = ' + str(id))
    MYSQL.connection.commit()

def create_comments(id_post, name, content):
    cur = MYSQL.connection.cursor()
    cur.execute('insert into comments (id_post, name, content) values (%s, %s, %s)', (id_post, name, content))
    MYSQL.connection.commit()

def get_comments():
    cur = MYSQL.connection.cursor()
    cur.execute('select * from comments order by FechaCreacion')
    comments = cur.fetchall()
    return comments


if __name__ == '__main__':
    APP.run(
        debug = True
    )
