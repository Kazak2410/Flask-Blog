from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from blog import db, bcrypt
from blog.models import User, Post
from blog.users.forms import (RegisterForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm)
from blog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have just been registered!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form, title='Register')


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have just been loged in!', 'success')
            return redirect(url_for('posts.home'))
        else:
            flash('Login Unsuccessful. Check your email and password', 'danger')
    return render_template('login.html', form=form, title='LogIn')


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('posts.home'))


@users.route('/account/<int:user_id>')
def account(user_id):
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    image_file = url_for('static', filename='images/' + user.image_file)
    return render_template('account.html', user=user, posts=posts, image_file=image_file, title='Account')

@users.route('/update_activity', methods=['POST'])
@login_required
def update_activity():
    data = request.get_json()
    last_activity = datetime.fromtimestamp(int(data['last_activity'])/1000.0)
    user_activity = User.query.filter_by(id=current_user.id).first()
    user_activity.last_activity =  last_activity
    db.session.commit()
    return 'OK'


@users.route('/update_account', methods=['GET', 'POST'])
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account', user_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('update_account.html', form=form, title='Account')


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@users.route('/reset_request/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form, title='Reset Password')
