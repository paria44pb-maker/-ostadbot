import ast
import operator as op

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def eval_expr(expression: str):
    try:
        expression = expression.strip().replace("^", "**")
        node = ast.parse(expression, mode="eval").body
        return _eval(node)
    except Exception:
        return None

def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError("Only int/float allowed")

    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise TypeError("Operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval(node.left), _eval(node.right))

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise TypeError("Unary operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval(node.operand))

    raise TypeError("Unsupported expression")
