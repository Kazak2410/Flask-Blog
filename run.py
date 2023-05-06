from blog import app


def run_app():
    with app.app_context():
        if __name__ == '__main__':
            app.run(debug=True)


run_app()
