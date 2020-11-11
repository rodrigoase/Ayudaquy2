from app import MYSQL

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
