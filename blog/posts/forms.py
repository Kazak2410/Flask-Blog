from blog import app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from blog.models import Category


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(3, 100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    with app.app_context():
        category = SelectField('Category', choices=[(category.name, category.name) for category in Category.query.all()])
    submit = SubmitField('Create')


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
