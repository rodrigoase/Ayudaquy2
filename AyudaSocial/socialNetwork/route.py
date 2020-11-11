from flask import request, render_template, flash, redirect, url_for
from app import MYSQL, APP
from .models import create_post, get_posts, delete_post, create_comments, get_comments

@APP.route('/post', methods=['GET','POST'])
def posts():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        name = request.form.get('name')
        post = request.form.get('post')
        if len(name) > 0 and len(post) > 0:
            create_post(str(name), str(post))
            flash('Se acaba de publicar tu mensaje!', 'success')
        else:
            flash('Post no se pudo publicar', 'danger')
    posts = get_posts()
    comments = get_comments()
    return render_template('index.html', posts= posts, comments=comments)


@APP.route('/delete/<int:id>', methods=['POST','GET'])
def delete(id):
    posts = get_posts()
    if request.method == 'POST':
        delete_post(id)
        flash('Publicación eliminada', 'success')
        return redirect(url_for('posts'))

@APP.route('/comment', methods=['POST'])
def comments():
    if request.method == 'POST':
        id_post = request.form.get('id_post')
        name = request.form.get('name')
        content = request.form.get('content')
        create_comments(id_post,name,content)
        return redirect(url_for('posts'))

