import os
from datetime import datetime
from flask import render_template, url_for, flash, redirect, abort, request
from blog import app, db, bcrypt, mail
from blog.forms import RegisterForm, LoginForm, PostForm, RequestResetForm, ResetPasswordForm
from blog.models import User, Post, Category
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message


@app.route('/')
def home():
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('home.html', posts=posts, categories=categories, title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have just been registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have just been loged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Check your email and password', 'danger')
    return render_template('login.html', form=form, title='LogIn')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.category.data).first()
        post = Post(title=form.title.data, content=form.content.data, author=current_user, category=category)
        db.session.add(post)
        db.session.commit()
        flash('The post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form, title='CreatPost')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title=post.title)


@app.route('/account/<int:user_id>')
@login_required
def account(user_id):
    user = User.query.get(user_id)
    return render_template('account.html', user=user, title='Account')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form)


@app.route('/update_activity', methods=['POST'])
@login_required
def update_activity():
    data = request.get_json()
    last_activity = datetime.fromtimestamp(int(data['last_activity'])/1000.0)
    user_activity = User.query.filter_by(id=current_user.id).first()
    user_activity.last_activity =  last_activity
    db.session.commit()
    return 'OK'


@app.route('/category/<int:category_id>/')
def category(category_id):
    posts = Post.query.filter_by(category_id=category_id)
    category_name = Category.query.filter_by(id=category_id).first().name
    categories = Category.query.all()
    return render_template('category.html', posts=posts, categories=categories, title=category_name)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@app.route('/reset_request/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form, title='Reset Password')
