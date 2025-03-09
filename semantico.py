import flet as ft
import ast

class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.defined_variables = {}
        self.used_variables = set()
        self.defined_functions = {}
        self.result_message = ""
        self.builtins = set(dir(__builtins__))  

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            self.defined_variables[var_name] = self.get_type(node.value)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
            if node.id not in self.defined_variables and node.id not in self.builtins:
                self.errors.append(f"Error semántico: Variable '{node.id}' no definida.")
        self.generic_visit(node)

    def visit_BinOp(self, node):
        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)
        
        if isinstance(node.op, ast.Div) and right_type == 'int' and isinstance(node.right, ast.Constant):
            if node.right.value == 0:
                self.errors.append("Error semántico: División por cero.")
        
        if left_type and right_type and left_type != right_type:
            self.errors.append("Error semántico: Operación entre tipos incompatibles.")
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name in ('if', 'else', 'while', 'return'):
            self.errors.append(f"Error semántico: '{node.name}' es una palabra clave reservada.")
        self.defined_functions[node.name] = len(node.args.args)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            num_args = len(node.args)
            if func_name in self.defined_functions:
                expected_args = self.defined_functions[func_name]
                if num_args != expected_args:
                    self.errors.append(f"Error semántico: La función '{func_name}' esperaba {expected_args} argumentos, pero recibió {num_args}.")
        self.generic_visit(node)
    
    def visit_Return(self, node):
        if not isinstance(node.parent, ast.FunctionDef):
            self.errors.append("Error semántico: 'return' usado fuera de una función.")
        self.generic_visit(node)
    
    def visit_If(self, node):
        condition_type = self.get_type(node.test)
        if condition_type and condition_type not in ['bool', 'int']:
            self.errors.append("Error semántico: Condición en 'if' no es booleana ni entera.")
        self.generic_visit(node)
    
    def visit_While(self, node):
        condition_type = self.get_type(node.test)
        if condition_type and condition_type not in ['bool', 'int']:
            self.errors.append("Error semántico: Condición en 'while' no es booleana ni entera.")
        
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.errors.append("Error semántico: Bucle 'while True' sin 'break', posible bucle infinito.")
        
        self.generic_visit(node)
    
    def get_type(self, node):
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.Name) and node.id in self.defined_variables:
            return self.defined_variables[node.id]
        return None

    def analyze(self, source_code):
        self.errors = []
        self.defined_variables.clear()
        self.used_variables.clear()
        self.defined_functions.clear()
        self.result_message = "Código analizado correctamente. No se encontraron errores semánticos."
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent = node  # Agregar referencia al nodo padre
            self.visit(tree)
            
           
            unused_vars = set(self.defined_variables.keys()) - self.used_variables
            for var in unused_vars:
                self.errors.append(f"Advertencia: Variable '{var}' declarada pero no utilizada.")
        except Exception as e:
            self.errors.append(f"Error de análisis: {e}")
            self.result_message = ""
        if self.errors:
            self.result_message = "\n".join(self.errors)
        return self.result_message

def main(page: ft.Page):
    page.title = "Analizador Semántico braulio binet 2-18-0796"
    page.window_width = 500
    page.window_height = 400
    
    input_code = ft.TextField(label="Código fuente", multiline=True, width=400, height=150)
    output_result = ft.Text(value="", color="green", size=14)
    
    analyzer = SemanticAnalyzer()
    
    def analyze_code(e):
        result = analyzer.analyze(input_code.value)
        output_result.value = result
        output_result.color = "red" if "Error" in result else "green"
        page.update()
    
    analyze_button = ft.ElevatedButton("Analizar", on_click=analyze_code)
    
    page.add(input_code, analyze_button, output_result)

ft.app(target=main)
