from flask_wtf import FlaskForm
from blog import app
from wtforms import StringField, EmailField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from blog.models import User, Category


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(2, 25)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            ValidationError('This user name is already in use! Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            ValidationError('This email is already in use! Please choose a different one.')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(3, 100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    with app.app_context():
        category = SelectField('Category', choices=[(category.name, category.name) for category in Category.query.all()])
    submit = SubmitField('Create')
