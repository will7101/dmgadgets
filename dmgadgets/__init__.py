from flask import Flask, request, render_template, json
from .boolexp import AST, BoolExpError

app = Flask(__name__)


@app.route('/hello')
def hello():
    return 'Hello, World!'


@app.route('/', methods=['GET', 'POST'])
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
    if len(expr) > 500:
        return 400

    op_table = {}
    for i in range(5):
        op_table[request.args['op%d' % i]] = i

    tree = AST(op_table)
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
    dnf = (dnf[0] if dnf[0] else '空') + '<br>' + str(dnf[1])
    cnf = tree.cnf(truth)
    cnf = (cnf[0] if cnf[0] else '空') + '<br>' + str(cnf[1])
    image = tree.dump_graph()
    # print(image)

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
        'truth_table': truth,
        'image': image
    })


@app.route('/api/from-truth-table', methods=['GET'])
def from_truth_table():
    var_num = int(request.args['var_num'])
    if var_num > 6:
        return 400
    table = []
    for binary in range(2 ** var_num):
        row = {}
        for i in range(var_num):
            var_name = chr(65 + i)
            var_val = (binary >> (var_num - i - 1)) & 1
            row[var_name] = bool(var_val)
        row['result'] = bool(int(request.args['val' + str(binary)]))
        table.append(row)

    tree = AST()
    tree.var_names = list("ABCDEF"[:var_num])
    dnf = tree.dnf(table)
    dnf = (dnf[0] if dnf[0] else '空') + '<br>' + str(dnf[1])
    cnf = tree.cnf(table)
    cnf = (cnf[0] if cnf[0] else '空') + '<br>' + str(cnf[1])
    expr = tree.simplify(table)
    tree.parse(expr)
    image = tree.dump_graph()

    return json.dumps({
        'status': 'ok',
        'result_list': [
            {
                'title': '主析取范式',
                'content': dnf
            },
            {
                'title': '主合取范式',
                'content': cnf
            },
            {
                'title': '简化后的表达式',
                'content': expr
            }
        ],
        'image': image
    })
