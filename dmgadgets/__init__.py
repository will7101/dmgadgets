from flask import Flask, request, render_template, json
from .boolexp import AST, BoolExpError

app = Flask(__name__)


@app.route('/hello')
def hello():
    return 'Hello, World!'


@app.route('/calc', methods=['GET', 'POST'])
def calc():
    if request.method == 'POST':
        # print(dict(request.form))
        tree = AST()
        tree.parse(request.form['expr'])
        table = tree.truth_table()
        msg = '主析取范式：%r，主合取范式：%r' % (tree.dnf(table), tree.cnf(table))
        return render_template('calc.html', msg=msg)
    else:
        return render_template('calc.html')


@app.route('/api/parse', methods=['GET'])
def parse():
    expr = request.args['expr']
    tree = AST()
    try:
        tree.parse(expr)
    except BoolExpError as err:
        return json.dumps({
            'status': 'failed',
            'msg': str(err)
        })

    var_names = tree.var_names
    truth = tree.truth_table()
    pn = ' '.join(tree.traversal(0))
    rpn = ' '.join(tree.traversal(2))
    dnf = tree.dnf(truth)
    dnf = dnf[0] + '<br>' + str(dnf[1])
    cnf = tree.cnf(truth)
    cnf = cnf[0] + '<br>' + str(cnf[1])

    return json.dumps({
        'status': 'ok',
        'result_list': [
            {
                'title': '波兰表达式',
                'content': pn
            },
            {
                'title': '逆波兰表达式',
                'content': rpn
            },
            {
                'title': '主析取范式',
                'content': dnf
            },
            {
                'title': '主合取范式',
                'content': cnf
            },
        ],
        'var_names': var_names,
        'truth_table': truth
    })
