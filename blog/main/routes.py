from flask import render_template, Blueprint


main = Blueprint('main', __name__)


@main.route('/about')
def about():
    return render_template('about.html')
