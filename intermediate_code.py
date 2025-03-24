"""
Intermediate code generator module with optimization and detailed information.
"""
from typing import List, Dict, Optional, Union
from .lexer import TokenType
from .parser import ASTNode, BinOpNode, NumNode, VarNode, AssignNode, PrintNode, IfNode, WhileNode
from .symbol_table import SymbolType

class ThreeAddressCode:
    def __init__(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, 
                 result: Optional[str] = None, line: int = 0, comment: str = ""):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        self.line = line
        self.comment = comment
    
    def __str__(self):
        if self.op == ':=':
            base = f"{self.result} := {self.arg1}"
        elif self.op in ('+', '-', '*', '/'):
            base = f"{self.result} := {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'PRINT':
            base = f"PRINT {self.arg1}"
        elif self.op == 'CMP':
            base = f"CMP {self.arg1} {self.arg2}"
        elif self.op == 'JZ':
            base = f"JZ {self.arg1} {self.arg2}"
        elif self.op == 'JMP':
            base = f"JMP {self.arg1}"
        elif self.op == 'LABEL':
            base = f"{self.arg1}:"
        elif self.op == 'LOAD':
            base = f"LOAD {self.arg1}"
        elif self.op == 'ASSIGN':
            base = f"{self.result} := {self.arg1}"
        elif self.op in ('ADD', 'SUB', 'MUL', 'DIV'):
            base = f"{self.result} := {self.arg1} {self.op} {self.arg2}"
        elif self.op in ('GT', 'LT', 'EQ'):
            base = f"{self.result} := {self.arg1} {self.op} {self.arg2}"
        else:
            base = f"{self.op} {self.arg1 or ''} {self.arg2 or ''} {self.result or ''}"
        
        if self.comment:
            return f"{base:<30} # {self.comment}"
        return base

class IntermediateCodeGenerator:
    def __init__(self):
        self.code: List[ThreeAddressCode] = []
        self.temp_counter = 0
        self.current_line = 0
        self.optimizations = {
            'constant_folding': True,
            'copy_propagation': True
        }
        self.value_table: Dict[str, Union[int, float, str]] = {}
        self.label_counter = 0
    
    def get_temp(self) -> str:
        """Generate a new temporary variable name."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def get_label(self) -> str:
        """Generate a new label name."""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def add_instruction(self, op: str, arg1: Optional[str] = None, 
                       arg2: Optional[str] = None, result: Optional[str] = None, 
                       comment: str = "") -> str:
        """Add a new instruction with optional comment."""
        instr = ThreeAddressCode(op, arg1, arg2, result, self.current_line, comment)
        self.code.append(instr)
        return result if result else ""
    
    def generate(self, ast):
        """Generate intermediate code from AST."""
        if isinstance(ast, list):
            for node in ast:
                self.generate(node)
        elif isinstance(ast, AssignNode):
            self.generate_assignment(ast)
        elif isinstance(ast, BinOpNode):
            self.generate_bin_op(ast)
        elif isinstance(ast, VarNode):
            self.generate_variable(ast)
        elif isinstance(ast, NumNode):
            self.generate_number(ast)
        elif isinstance(ast, PrintNode):
            self.generate_print(ast)
        elif isinstance(ast, IfNode):
            self.generate_if(ast)
        elif isinstance(ast, WhileNode):
            self.generate_while(ast)

    def generate_assignment(self, node):
        """Generate code for assignment."""
        # Generar código para el lado derecho
        if isinstance(node.right, BinOpNode):
            result = self.generate_bin_op(node.right)
        elif isinstance(node.right, VarNode):
            result = self.generate_variable(node.right)
        elif isinstance(node.right, NumNode):
            result = str(node.right.value)
        else:
            result = None

        # Generar la asignación
        if result:
            self.add_instruction("ASSIGN", result, None, node.left.value, f"Assign {result} to {node.left.value}")
            self.value_table[node.left.value] = result
        else:
            self.add_instruction("ASSIGN", str(node.right.value), None, node.left.value, f"Assign {node.right.value} to {node.left.value}")
            self.value_table[node.left.value] = str(node.right.value)

    def generate_bin_op(self, node):
        """Generate code for binary operation."""
        # Generar código para el lado izquierdo
        if isinstance(node.left, BinOpNode):
            left = self.generate_bin_op(node.left)
        elif isinstance(node.left, VarNode):
            left = self.generate_variable(node.left)
        elif isinstance(node.left, NumNode):
            left = self.generate_number(node.left)
        else:
            left = str(node.left.value)

        # Generar código para el lado derecho
        if isinstance(node.right, BinOpNode):
            right = self.generate_bin_op(node.right)
        elif isinstance(node.right, VarNode):
            right = self.generate_variable(node.right)
        elif isinstance(node.right, NumNode):
            right = self.generate_number(node.right)
        else:
            right = str(node.right.value)

        # Generar la operación
        if node.op.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
            result = self.get_temp()
            op = {
                TokenType.PLUS: "ADD",
                TokenType.MINUS: "SUB",
                TokenType.MULTIPLY: "MUL",
                TokenType.DIVIDE: "DIV"
            }[node.op.type]
            self.add_instruction(op, left, right, result, f"Perform {op} operation")
            return result
        elif node.op.type in (TokenType.GREATER_THAN, TokenType.LESS_THAN, TokenType.EQUALS):
            result = self.get_temp()
            op = {
                TokenType.GREATER_THAN: "GT",
                TokenType.LESS_THAN: "LT",
                TokenType.EQUALS: "EQ"
            }[node.op.type]
            self.add_instruction(op, left, right, result, f"Compare {left} {op} {right}")
            return result
        return None

    def generate_variable(self, node):
        """Generate code for variable reference."""
        # Si la variable ya tiene un valor conocido, usarlo directamente
        if node.value in self.value_table and self.value_table[node.value] is not None:
            return str(self.value_table[node.value])
        
        # Si no, cargar la variable
        self.add_instruction("LOAD", node.value, None, None, f"Load variable {node.value}")
        return node.value

    def generate_number(self, node):
        """Generate code for number literal."""
        self.add_instruction("LOAD", str(node.value), None, None, f"Load constant {node.value}")
        return str(node.value)

    def generate_print(self, node):
        """Generate code for print statement."""
        if isinstance(node.value, VarNode):
            self.add_instruction("PRINT", node.value.value, None, None, f"Print variable {node.value.value}")
        elif isinstance(node.value, NumNode):
            self.add_instruction("PRINT", str(node.value.value), None, None, f"Print constant {node.value.value}")
        elif isinstance(node.value, BinOpNode):
            result = self.generate_bin_op(node.value)
            if result:
                self.add_instruction("PRINT", result, None, None, f"Print expression result")

    def generate_if(self, node):
        """Generate code for if statement."""
        # Generar código para la condición
        if isinstance(node.condition, BinOpNode):
            condition = self.generate_bin_op(node.condition)
            # Generar comparación
            if node.condition.op.type in (TokenType.GREATER_THAN, TokenType.LESS_THAN, TokenType.EQUALS):
                self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")
        elif isinstance(node.condition, VarNode):
            condition = self.generate_variable(node.condition)
            self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")
        else:
            condition = str(node.condition.value)
            self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")

        # Generar etiquetas
        else_label = self.get_label()
        end_label = self.get_label()

        # Generar salto condicional
        self.add_instruction("JZ", condition, else_label, None, f"If {condition} is false, jump to else")
        
        # Generar código para el cuerpo del if
        for stmt in node.then_body:
            self.generate(stmt)
        
        # Generar salto al final
        self.add_instruction("JMP", end_label, None, None, "Jump to end of if")
        
        # Generar etiqueta else
        self.add_instruction("LABEL", else_label, None, None, "Else branch")
        
        # Generar código para el else si existe
        if node.else_body:
            for stmt in node.else_body:
                self.generate(stmt)
        
        # Generar etiqueta final
        self.add_instruction("LABEL", end_label, None, None, "End of if")

    def generate_while(self, node):
        """Generate code for while statement."""
        # Generar etiquetas
        start_label = self.get_label()
        end_label = self.get_label()
        
        # Generar etiqueta de inicio del bucle
        self.add_instruction("LABEL", start_label, None, None, "Start of while loop")
        
        # Generar código para la condición
        if isinstance(node.condition, BinOpNode):
            condition = self.generate_bin_op(node.condition)
            # Generar comparación
            if node.condition.op.type in (TokenType.GREATER_THAN, TokenType.LESS_THAN, TokenType.EQUALS):
                self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")
        elif isinstance(node.condition, VarNode):
            condition = self.generate_variable(node.condition)
            self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")
        else:
            condition = str(node.condition.value)
            self.add_instruction("CMP", condition, "0", None, f"Compare {condition} with 0")
        
        # Generar salto condicional
        self.add_instruction("JZ", condition, end_label, None, f"If {condition} is false, exit loop")
        
        # Generar código para el cuerpo del bucle
        for stmt in node.body:
            self.generate(stmt)
        
        # Generar salto al inicio del bucle
        self.add_instruction("JMP", start_label, None, None, "Jump back to start of loop")
        
        # Generar etiqueta final
        self.add_instruction("LABEL", end_label, None, None, "End of while loop")
    
    def get_code(self) -> List[ThreeAddressCode]:
        """Get the generated intermediate code."""
        return self.code 