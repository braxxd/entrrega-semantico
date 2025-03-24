from .lexer import Lexer, TokenType
from .symbol_table import SymbolTable
from typing import Optional

class ASTNode:
    pass

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class NumNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class VarNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class AssignNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Parser:
    def __init__(self, lexer: Lexer, symbol_table: SymbolTable):
        self.lexer = lexer
        self.symbol_table = symbol_table
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        raise Exception(f'{message} at line {self.current_token.line}, column {self.current_token.column}')
    
    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'Expected {token_type}, got {self.current_token.type}')
    
    def program(self):
        """program : PROGRAM variable_declarations compound_statement"""
        self.eat(TokenType.PROGRAM)
        # Skip empty lines after PROGRAM
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        
        # Process variable declarations
        declarations = self.variable_declarations()
        
        # Process compound statement
        statements = self.compound_statement()
        
        # Combine declarations and statements
        return declarations + statements
    
    def variable_declarations(self):
        """variable_declarations : VAR (variable_declaration SEMICOLON)*"""
        declarations = []
        if self.current_token.type == TokenType.VAR:
            self.eat(TokenType.VAR)
            while self.current_token.type == TokenType.IDENTIFIER:
                declarations.extend(self.variable_declaration())
                self.eat(TokenType.SEMICOLON)
                # Skip empty lines
                while self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
        return declarations
    
    def variable_declaration(self):
        """variable_declaration : ID (ASSIGN expr)?"""
        var_nodes = []
        # Get the current token before eating it
        token = self.current_token
        var_node = VarNode(token)
        var_nodes.append(var_node)
        
        # Add the variable to the symbol table with initial value None
        self.symbol_table.insert(token.value, None, token.line)
        
        self.eat(TokenType.IDENTIFIER)
        
        # Check for initialization
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            right = self.expr()
            
            # Update the symbol table with the initial value
            if isinstance(right, NumNode):
                if right.token.type == TokenType.STRING_LITERAL:
                    self.symbol_table.insert(var_node.value, right.value, token.line)
                else:
                    try:
                        value = float(right.value) if isinstance(right.value, str) and '.' in right.value else int(right.value)
                        self.symbol_table.insert(var_node.value, value, token.line)
                    except ValueError:
                        self.error(f"Invalid numeric value: {right.value}")
            elif isinstance(right, VarNode):
                right_symbol = self.symbol_table.lookup(right.value, record_usage=True, line=token.line)
                if right_symbol and right_symbol.value is not None:
                    self.symbol_table.insert(var_node.value, right_symbol.value, token.line)
            
            # Registrar el uso de la variable en la asignación
            self.symbol_table.lookup(var_node.value, record_usage=True, line=token.line)
            return [AssignNode(var_node, right)]
        
        # Si no hay inicialización, registrar el uso de la variable
        self.symbol_table.lookup(var_node.value, record_usage=True, line=token.line)
        return var_nodes
    
    def compound_statement(self):
        """compound_statement : statement (SEMICOLON statement)*"""
        nodes = []
        # Skip initial empty lines
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        
        # Add first non-empty statement
        if self.current_token.type != TokenType.EOF:
            nodes.append(self.statement())
        
        # Add remaining statements
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            # Skip empty lines
            while self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            if self.current_token.type != TokenType.EOF:
                nodes.append(self.statement())
        
        return nodes
    
    def statement(self):
        """
        statement : assignment_statement
                 | print_statement
                 | if_statement
                 | while_statement
                 | empty
        """
        if self.current_token.type == TokenType.IDENTIFIER:
            return self.assignment_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.print_statement()
        elif self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.type == TokenType.VAR:
            return self.variable_declarations()
        else:
            return self.empty()
    
    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        
        # Update the symbol table with the assigned value and line information
        if isinstance(right, NumNode):
            if right.token.type == TokenType.STRING_LITERAL:
                self.symbol_table.insert(left.value, right.value, token.line)
            else:
                try:
                    value = float(right.value) if isinstance(right.value, str) and '.' in right.value else int(right.value)
                    self.symbol_table.insert(left.value, value, token.line)
                except ValueError:
                    self.error(f"Invalid numeric value: {right.value}")
        elif isinstance(right, VarNode):
            right_symbol = self.symbol_table.lookup(right.value, record_usage=True, line=token.line)
            if right_symbol and right_symbol.value is not None:
                self.symbol_table.insert(left.value, right_symbol.value, token.line)
        elif isinstance(right, BinOpNode):
            symbol = self.symbol_table.lookup(left.value, record_usage=False)
            if symbol:
                expr = self._build_expression(right)
                symbol.set_expression(expr)
                symbol.info.last_modified_line = token.line
                try:
                    result = self._evaluate_expression(right)
                    if result is not None:
                        symbol.update_value(result, token.line)
                except:
                    pass
        
        # Registrar el uso de la variable en la asignación
        self.symbol_table.lookup(left.value, record_usage=True, line=token.line)
        return AssignNode(left, right)
    
    def _evaluate_expression(self, node: BinOpNode) -> Optional[float]:
        """Evaluate a binary operation if possible"""
        if isinstance(node, NumNode):
            return float(node.value) if '.' in str(node.value) else int(node.value)
        elif isinstance(node, VarNode):
            symbol = self.symbol_table.lookup(node.value, record_usage=True, line=self.current_token.line)
            if symbol and symbol.value is not None:
                return symbol.value
            return None
        elif isinstance(node, BinOpNode):
            left = self._evaluate_expression(node.left)
            right = self._evaluate_expression(node.right)
            if left is not None and right is not None:
                if node.op.type == TokenType.PLUS:
                    return left + right
                elif node.op.type == TokenType.MINUS:
                    return left - right
                elif node.op.type == TokenType.MULTIPLY:
                    return left * right
                elif node.op.type == TokenType.DIVIDE:
                    return left / right if right != 0 else None
        return None
    
    def _build_expression(self, node: BinOpNode) -> str:
        """Build a string representation of an expression"""
        if isinstance(node, NumNode):
            return str(node.value)
        elif isinstance(node, VarNode):
            # Record variable usage in expressions
            self.symbol_table.lookup(node.value, record_usage=True, line=self.current_token.line)
            return node.value
        elif isinstance(node, BinOpNode):
            left = self._build_expression(node.left)
            right = self._build_expression(node.right)
            op = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.MULTIPLY: '*',
                TokenType.DIVIDE: '/'
            }.get(node.op.type, '?')
            return f"({left} {op} {right})"
        return ""
    
    def variable(self):
        """variable : ID"""
        node = VarNode(self.current_token)
        
        # Verify that the variable exists in the symbol table and record usage
        symbol = self.symbol_table.lookup(self.current_token.value, record_usage=True, line=self.current_token.line)
        if not symbol:
            self.error(f"Variable '{self.current_token.value}' not declared")
        
        self.eat(TokenType.IDENTIFIER)
        return node
    
    def empty(self):
        """empty :"""
        return None
    
    def expr(self):
        """expr : term ((PLUS | MINUS | GREATER_THAN | LESS_THAN | EQUALS) term)*"""
        node = self.term()
        
        # Registrar uso de variables en el primer término
        if isinstance(node, VarNode):
            self.symbol_table.lookup(node.value, record_usage=True, line=self.current_token.line)
        elif isinstance(node, BinOpNode):
            self._register_variable_usage_in_expr(node)
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS, 
                                        TokenType.GREATER_THAN, TokenType.LESS_THAN, 
                                        TokenType.EQUALS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            elif token.type == TokenType.GREATER_THAN:
                self.eat(TokenType.GREATER_THAN)
            elif token.type == TokenType.LESS_THAN:
                self.eat(TokenType.LESS_THAN)
            elif token.type == TokenType.EQUALS:
                self.eat(TokenType.EQUALS)
            
            right = self.term()
            node = BinOpNode(node, token, right)
            
            # Registrar uso de variables en la expresión
            if isinstance(node.left, VarNode):
                self.symbol_table.lookup(node.left.value, record_usage=True, line=self.current_token.line)
            elif isinstance(node.left, BinOpNode):
                self._register_variable_usage_in_expr(node.left)
            
            if isinstance(node.right, VarNode):
                self.symbol_table.lookup(node.right.value, record_usage=True, line=self.current_token.line)
            elif isinstance(node.right, BinOpNode):
                self._register_variable_usage_in_expr(node.right)
        
        return node
    
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            else:
                self.eat(TokenType.DIVIDE)
            
            node = BinOpNode(node, token, self.factor())
        
        return node
    
    def factor(self):
        """
        factor : PLUS factor
               | MINUS factor
               | INTEGER_CONST
               | FLOAT_CONST
               | STRING_LITERAL
               | LPAREN expr RPAREN
               | variable
        """
        token = self.current_token
        
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return self.factor()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return BinOpNode(NumNode(Token(TokenType.INTEGER_CONST, 0, token.line, token.column)), token, self.factor())
        elif token.type in (TokenType.INTEGER_CONST, TokenType.FLOAT_CONST, TokenType.STRING_LITERAL):
            self.eat(token.type)
            return NumNode(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
            return self.variable()
    
    def print_statement(self):
        """print_statement : PRINT LPAREN expr RPAREN SEMICOLON"""
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        value = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        return PrintNode(value)
    
    def if_statement(self):
        """if_statement : IF LPAREN expr RPAREN LBRACE statement_list RBRACE (ELSE LBRACE statement_list RBRACE)?"""
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        then_body = self.statement_list()
        self.eat(TokenType.RBRACE)
        
        else_body = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LBRACE)
            else_body = self.statement_list()
            self.eat(TokenType.RBRACE)
        
        return IfNode(condition, then_body, else_body)

    def while_statement(self):
        """while_statement : WHILE LPAREN expr RPAREN LBRACE statement_list RBRACE"""
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.statement_list()
        self.eat(TokenType.RBRACE)
        return WhileNode(condition, body)

    def _register_variable_usage_in_expr(self, node: BinOpNode):
        """Register variable usage in an expression."""
        if isinstance(node.left, VarNode):
            self.symbol_table.lookup(node.left.value, record_usage=True, line=self.current_token.line)
        elif isinstance(node.left, BinOpNode):
            self._register_variable_usage_in_expr(node.left)
            
        if isinstance(node.right, VarNode):
            self.symbol_table.lookup(node.right.value, record_usage=True, line=self.current_token.line)
        elif isinstance(node.right, BinOpNode):
            self._register_variable_usage_in_expr(node.right)

    def statement_list(self):
        """statement_list : statement (SEMICOLON statement)*"""
        statements = []
        # Skip initial empty lines
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        
        # Add first non-empty statement
        if self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        
        # Add remaining statements
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            # Skip empty lines
            while self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            if self.current_token.type != TokenType.EOF:
                statements.append(self.statement())
        
        return statements
    
    def parse(self):
        """Parse the input and return an AST."""
        return self.program() 