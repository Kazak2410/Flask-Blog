from flask import render_template, url_for, flash, redirect
from blog import app, db, bcrypt
from blog.forms import RegisterForm, LoginForm
from blog.models import User
from flask_login import login_user, logout_user, login_required, current_user



@app.route('/')
def home():
    return render_template('home.html')


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
    return render_template('register.html', form=form)


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
    return render_template('login.html', form=form)
