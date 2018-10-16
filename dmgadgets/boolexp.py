import collections
import itertools
from typing import List

from graphviz import Graph
from flask import g
from base64 import b64encode

BoolOperator = collections.namedtuple('BoolOperator', ['func', 'privilege'])

#################################
# Constants
OP_NOT = 0
OP_AND = 1
OP_OR = 2
OP_IMP = 3
OP_EQ = 4

op_list = [OP_NOT, OP_AND, OP_OR, OP_IMP, OP_EQ]

op_func = [
    lambda _, y: not y,  # OP_NOT
    lambda x, y: x and y,  # OP_AND
    lambda x, y: x or y,  # OP_OR
    lambda x, y: not x or y,  # OP_IMP
    lambda x, y: x == y,  # OP_EQ
]

op_privilege = [5, 4, 3, 2, 1]


##################################


class BoolExpError(Exception):
    """Raise when an syntax error occurs in the expression
    """


class AST:
    """A class of Abstract Syntax Trees.
    """

    def __init__(self, op_table=None):
        self.root = None
        self.var_names = []
        self.var_table = {}

        if op_table is None:
            op_table = {
                '!': OP_NOT,
                '&': OP_AND,
                '|': OP_OR,
                '^': OP_IMP,
                '~': OP_EQ,
            }

        g.op_table = dict(op_table)
        g.op_table_r = {}
        for symbol, op in g.op_table.items():
            g.op_table_r[op] = symbol

    def __build_rpn(self, expr: str):
        """Build the Reverse Polish Notation from the expression
        """
        pos = 0

        def next_token():
            """Return the next token in the string. Return None if reached end.
            """
            nonlocal pos
            if pos >= len(expr):
                return None
            try:
                while expr[pos].isspace():
                    pos += 1
            except IndexError:
                return None

            token = expr[pos]
            pos += 1
            if token in g.op_table.keys():
                token = g.op_table[token]

            return token

        stack = []
        rpn = []
        while pos < len(expr):
            token = next_token()
            if token is None:
                break
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack[-1] != '(':
                    rpn.append(stack.pop())
                stack.pop()
            elif token in op_list:
                if token == OP_NOT:
                    while len(stack) != 0 and stack[-1] != '(' and op_privilege[stack[-1]] > op_privilege[token]:
                        rpn.append(stack.pop())
                else:
                    while len(stack) != 0 and stack[-1] != '(' and op_privilege[stack[-1]] >= op_privilege[token]:
                        rpn.append(stack.pop())
                stack.append(token)
            else:
                rpn.append(token)

        rpn.extend(reversed(stack))
        print(rpn)
        return rpn

    def __build_ast(self, rpn: list):
        """Build the tree from RPN.
        """
        stack = []
        self.var_table = {}
        for token in rpn:
            if token in op_list:
                node = OperatorNode(token)
                try:
                    if token == OP_NOT:
                        node.right = stack.pop()
                        node.left = DummyNode(False)
                    else:
                        node.right = stack.pop()
                        node.left = stack.pop()
                except IndexError:
                    raise BoolExpError('syntax error')
                stack.append(node)
            else:
                self.var_names.append(token)
                node = OperandNode(token)
                stack.append(node)
        if len(stack) != 1:
            raise BoolExpError('syntax error')
        self.var_names = sorted(set(self.var_names))  # sort and unique-fy
        if len(self.var_names) > 10:
            raise BoolExpError('too many variables')
        self.root = stack.pop()

    def parse(self, expr: str):
        """Parse an boolean expression and build the tree.
        """
        rpn = self.__build_rpn(expr)
        self.__build_ast(rpn)

    def eval(self):
        """Evaluate the value of the expression.
        """
        if self.root is None:
            return None
        value = self.root.eval(self.var_table)
        return value

    def traversal(self, order=0):
        """
        Return the depth-first traversal on the subtree in:

        0 = pre-order
        1 = in-order
        2 = post-order
        """
        result = []
        self.root.traversal(result, order)
        return result

    def truth_table(self):
        """
        Returns the truth table of the expression.

        table[$cond][$var_name] indicates the value of $var_name in condition $cond
        (in binary, 0 for False and 1 for True).

        table[$cond]['result'] indicates the value of the expression.
        """
        var_names = self.var_names
        num_vars = len(var_names)

        table = []
        for var_values in itertools.product([False, True], repeat=num_vars):
            for var_name, var_value in zip(var_names, var_values):
                self.var_table[var_name] = var_value
            row = dict(self.var_table)
            row['result'] = self.eval()
            table.append(row)
        return table

    def dnf(self, table):
        """
        Return the Principle Disjunctive Normal Form of the expression indicated by the truth table.

        Return a tuple of a literal expression and a list of minterms' indices
        """
        result = []
        indices = []
        for row in table:
            if row['result']:
                index = 0
                term = []
                for var in self.var_names:
                    index = index * 2 + int(row[var])
                    if not row[var]:
                        term.append(g.op_table_r[OP_NOT] + var)
                    else:
                        term.append(var)
                    term.append(g.op_table_r[OP_AND])
                term.pop()
                term = '(' + ' '.join(term) + ')'
                result.append(term)
                result.append(g.op_table_r[OP_OR])

                indices.append(index)
        result.pop()
        result = ' '.join(result)
        return result, indices

    def cnf(self, table):
        """
        Return the Principle Conjunctive Normal Form of the expression indicated by the truth table.

        Return a tuple of a literal expression and a list of maxterms' indices
        """
        result = []
        indices = []
        for row in reversed(table):
            if not row['result']:
                index = 0
                term = []
                for var in self.var_names:
                    index = index * 2 + int(not row[var])
                    if row[var]:
                        term.append(g.op_table_r[OP_NOT] + var)
                    else:
                        term.append(var)
                    term.append(g.op_table_r[OP_OR])
                term.pop()
                term = '(' + ' '.join(term) + ')'
                result.append(term)
                result.append(g.op_table_r[OP_AND])

                indices.append(index)
        if len(result) > 0:
            result.pop()
        result = ' '.join(result)
        return result, indices

    def dump_graph(self):
        """
        Use graphviz to dump into an image.

        Return the base64-encoded string of a png file.
        """
        dot = Graph(format='png')
        self.root.dump_graph(dot)
        return b64encode(dot.pipe()).decode('utf-8')


class ASTNode:
    """A class of nodes of Abstract Syntax Trees.
    """

    def __init__(self, token):
        self.left = None  # left child
        self.right = None  # right child
        self.token = token

    def __str__(self):
        return str(self.token)

    def eval(self, var):
        """
        Evaluate the value of the subtree.

        var[$var_name] -> the value of $var_name
        """

    def traversal(self, result: list, order=0):
        """
        Return the depth-first traversal on the subtree in:

        0 = pre-order
        1 = in-order
        2 = post-order
        """
        if order == 0:
            result.append(str(self))
        if self.left:
            self.left.traversal(result, order)
        if order == 1:
            result.append(str(self))
        if self.right:
            self.right.traversal(result, order)
        if order == 2:
            result.append(str(self))

    def dump_graph(self, dot: Graph, fid=''):
        """Dump the subtree.
        """
        sid = str(id(self))
        dot.node(sid, str(self))
        if fid:
            dot.edge(fid, sid)
        self.left.dump_graph(dot, sid)
        self.right.dump_graph(dot, sid)


class OperatorNode(ASTNode):
    def __str__(self):
        return g.op_table_r[self.token]

    def eval(self, var):
        func = op_func[self.token]
        return func(self.left.eval(var), self.right.eval(var))


class OperandNode(ASTNode):
    def eval(self, var):
        value = var[self.token]
        return value

    def dump_graph(self, dot: Graph, fid=''):
        """Dump the subtree.
        """
        sid = str(id(self))
        dot.node(sid, str(self), shape='box')
        if fid:
            dot.edge(fid, sid)


class DummyNode(ASTNode):
    def eval(self, var):
        return self.token

    def traversal(self, *args, **kwargs):
        return

    def dump_graph(self, dot: Graph, fid=''):
        """Dump the subtree.
        """
        # sid = str(id(self))
        # dot.node(sid, style='invis')
        # if fid:
        #     dot.edge(fid, sid, style='invis')
        pass


def main():
    """Some tests.
    """
    tree = AST()
    tree.parse('A~B')
    # print(tree.eval())
    print(' '.join(tree.traversal(0)))
    print(' '.join(tree.traversal(1)))
    print(' '.join(tree.traversal(2)))
    table = tree.truth_table()
    print(table)
    print(tree.dnf(table))
    print(tree.cnf(table))


if __name__ == '__main__':
    main()
