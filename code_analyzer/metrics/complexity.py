import ast
import math
from typing import Dict, Any, List, Set

class ComplexityMetrics:
    def calculate_maintainability_index(self, code: str, complexity: float, num_functions: int) -> float:
        halstead = self.calculate_halstead_metrics(code)
        volume = halstead["volume"]
        loc = len(code.splitlines())
        avg_cc = complexity / max(num_functions, 1)
        mi = 171 - 5.2 * math.log(volume + 1) - 0.23 * avg_cc - 16.2 * math.log(loc + 1)
        return max(0, min(100, mi * 100 / 171))

    def calculate_halstead_metrics(self, code: str) -> Dict[str, float]:
        tree = ast.parse(code)
        visitor = HalsteadVisitor()
        visitor.visit(tree)
        n1 = len(visitor.operators)
        n2 = len(visitor.operands)
        N1 = visitor.operator_count
        N2 = visitor.operand_count
        if n1 == 0 or n2 == 0:
            return {"volume": 0, "difficulty": 0, "effort": 0}
        program_length = N1 + N2
        vocabulary = n1 + n2
        volume = program_length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 * N2) / (2 * n2) if n2 > 0 else 0
        effort = difficulty * volume
        return {"volume": volume, "difficulty": difficulty, "effort": effort}

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        self.functions: List[Dict[str, Any]] = []
        self._current_function = None
        self._class_name = None

    def visit_ClassDef(self, node):
        old_class_name = self._class_name
        self._class_name = node.name
        self.generic_visit(node)
        self._class_name = old_class_name

    def visit_FunctionDef(self, node):
        old_function = self._current_function
        name = f"{self._class_name}.{node.name}" if self._class_name else node.name
        self._current_function = {"name": name, "complexity": 1, "line_number": node.lineno}
        self.generic_visit(node)
        self.functions.append(self._current_function)
        self.complexity += self._current_function["complexity"] - 1
        self._current_function = old_function

    def visit_If(self, node):
        self._increment_complexity()
        self.generic_visit(node)

    def visit_While(self, node):
        self._increment_complexity()
        self.generic_visit(node)

    def visit_For(self, node):
        self._increment_complexity()
        self.generic_visit(node)

    def visit_Try(self, node):
        self._increment_complexity()
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)

    def _increment_complexity(self):
        if self._current_function:
            self._current_function["complexity"] += 1
        else:
            self.complexity += 1

class HalsteadVisitor(ast.NodeVisitor):
    def __init__(self):
        self.operators: Set[str] = set()
        self.operands: Set[str] = set()
        self.operator_count = 0
        self.operand_count = 0

    def visit_BinOp(self, node):
        self.operators.add(type(node.op).__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.operators.add(type(node.op).__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.operators.add(type(node.op).__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        for op in node.ops:
            self.operators.add(type(op).__name__)
            self.operator_count += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        self.operands.add(node.id)
        self.operand_count += 1

    def visit_Constant(self, node):
        self.operands.add(str(node.value))
        self.operand_count += 1