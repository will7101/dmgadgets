from flask import Flask, request, render_template
from .boolexp import AST


def create_app():
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/calc', methods=['GET', 'POST'])
    def calc():
        if request.method == 'POST':
            tree = AST()
            tree.parse(request.form['expr'])
            table = tree.truth_table()
            msg = '主析取范式：%r，主合取范式：%r' % (tree.dnf(table), tree.cnf(table))
            return render_template('calc.html', msg=msg)
        else:
            return render_template('calc.html')

    return app
