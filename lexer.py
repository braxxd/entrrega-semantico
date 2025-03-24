"""
Enhanced lexical analyzer with improved token recognition and error handling.
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

class TokenType(Enum):
    # Keywords
    PROGRAM = auto()
    VAR = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    DO = auto()
    FUNCTION = auto()
    RETURN = auto()
    PRINT = auto()
    
    # Data types
    INTEGER_CONST = auto()
    FLOAT_CONST = auto()
    STRING_LITERAL = auto()
    BOOL = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    
    # Comparison
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUALS = auto()
    GREATER_EQUALS = auto()
    
    # Logical operators
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Others
    IDENTIFIER = auto()
    COMMENT = auto()
    EOF = auto()
    ERROR = auto()
    TRUE = auto()
    FALSE = auto()

    def to_spanish(self) -> str:
        """Convert token type to Spanish label."""
        translations = {
            # Keywords
            TokenType.PROGRAM: "PROGRAMA",
            TokenType.VAR: "VARIABLE",
            TokenType.INT: "ENTERO",
            TokenType.FLOAT: "REAL",
            TokenType.STRING: "CADENA",
            TokenType.IF: "SI",
            TokenType.ELSE: "SINO",
            TokenType.WHILE: "MIENTRAS",
            TokenType.FOR: "PARA",
            TokenType.DO: "HACER",
            TokenType.FUNCTION: "FUNCION",
            TokenType.RETURN: "RETORNAR",
            TokenType.PRINT: "IMPRIMIR",
            
            # Data types
            TokenType.INTEGER_CONST: "CONSTANTE_ENTERA",
            TokenType.FLOAT_CONST: "CONSTANTE_REAL",
            TokenType.STRING_LITERAL: "CADENA_LITERAL",
            TokenType.BOOL: "BOOLEANO",
            
            # Operators
            TokenType.PLUS: "SUMA",
            TokenType.MINUS: "RESTA",
            TokenType.MULTIPLY: "MULTIPLICACION",
            TokenType.DIVIDE: "DIVISION",
            TokenType.MODULO: "MODULO",
            TokenType.ASSIGN: "ASIGNACION",
            
            # Comparison
            TokenType.EQUALS: "IGUAL",
            TokenType.NOT_EQUALS: "DIFERENTE",
            TokenType.LESS_THAN: "MENOR_QUE",
            TokenType.GREATER_THAN: "MAYOR_QUE",
            TokenType.LESS_EQUALS: "MENOR_IGUAL",
            TokenType.GREATER_EQUALS: "MAYOR_IGUAL",
            
            # Logical operators
            TokenType.AND: "Y",
            TokenType.OR: "O",
            TokenType.NOT: "NO",
            
            # Delimiters
            TokenType.LPAREN: "PARENTESIS_IZQ",
            TokenType.RPAREN: "PARENTESIS_DER",
            TokenType.LBRACE: "LLAVE_IZQ",
            TokenType.RBRACE: "LLAVE_DER",
            TokenType.LBRACKET: "CORCHETE_IZQ",
            TokenType.RBRACKET: "CORCHETE_DER",
            TokenType.SEMICOLON: "PUNTO_COMA",
            TokenType.COMMA: "COMA",
            TokenType.DOT: "PUNTO",
            TokenType.COLON: "DOS_PUNTOS",
            
            # Others
            TokenType.IDENTIFIER: "IDENTIFICADOR",
            TokenType.COMMENT: "COMENTARIO",
            TokenType.EOF: "FIN_ARCHIVO",
            TokenType.ERROR: "ERROR",
            TokenType.TRUE: "VERDADERO",
            TokenType.FALSE: "FALSO"
        }
        return translations.get(self, str(self))

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    error_message: Optional[str] = None

    def __str__(self) -> str:
        if self.error_message:
            return f"Token({self.type.to_spanish()}, '{self.value}', línea={self.line}, columna={self.column}, error='{self.error_message}')"
        return f"Token({self.type.to_spanish()}, '{self.value}', línea={self.line}, columna={self.column})"

class LexicalError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Error léxico: {message} en línea {line}, columna {column}")

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        self.error_count = 0  # Contador de errores
        self.warning_count = 0  # Contador de advertencias
        
        self.keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'string': TokenType.STRING,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'do': TokenType.DO,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }
    
    def error(self, message="Carácter inválido"):
        """Registra un error léxico."""
        self.error_count += 1
        raise LexicalError(message, self.line, self.column)
    
    def warning(self, message: str) -> Token:
        """Registra una advertencia léxica y retorna un token de error."""
        self.warning_count += 1
        return Token(
            type=TokenType.ERROR,
            value=self.current_char,
            line=self.line,
            column=self.column,
            error_message=message
        )
    
    def advance(self):
        """Avanza el cursor un carácter."""
        self.pos += 1
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def peek(self):
        """Mira el siguiente carácter sin avanzar."""
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None
    
    def peek_next(self):
        """Mira el segundo carácter siguiente sin avanzar."""
        peek_pos = self.pos + 2
        return self.text[peek_pos] if peek_pos < len(self.text) else None
    
    def skip_whitespace(self):
        """Salta caracteres en blanco."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        """Salta comentarios de una línea y múltiples líneas."""
        if self.current_char == '/' and self.peek() == '/':
            # Comentario de una línea
            while self.current_char and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            # Comentario de múltiples líneas
            self.advance()  # Salta /
            self.advance()  # Salta *
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # Salta *
                    self.advance()  # Salta /
                    break
                self.advance()
            if not self.current_char:
                self.error("Comentario multilínea no cerrado")
    
    def number(self):
        """Retorna un token numérico (entero o real)."""
        result = ''
        token_type = TokenType.INTEGER_CONST
        start_column = self.column
        has_decimal = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_decimal:
                    self.error("Número real inválido - múltiples puntos decimales")
                has_decimal = True
                token_type = TokenType.FLOAT_CONST
            result += self.current_char
            self.advance()
        
        try:
            value = float(result) if token_type == TokenType.FLOAT_CONST else int(result)
            return Token(
                type=token_type,
                value=value,
                line=self.line,
                column=start_column
            )
        except ValueError:
            self.error(f"Valor numérico inválido: {result}")
    
    def string(self):
        """Retorna un token de cadena."""
        result = ''
        start_column = self.column
        self.advance()  # Salta la comilla inicial
        
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char in {'n', 't', 'r', '"', '\\'}:
                    result += {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\'}[self.current_char]
                else:
                    self.error(f"Secuencia de escape inválida: \\{self.current_char}")
            else:
                result += self.current_char
            self.advance()
        
        if self.current_char != '"':
            self.error("Cadena no cerrada")
        
        self.advance()  # Salta la comilla final
        return Token(TokenType.STRING_LITERAL, result, self.line, start_column)
    
    def identifier(self):
        """Retorna un token identificador o palabra clave."""
        result = ''
        start_column = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Verificar longitud máxima del identificador
        if len(result) > 32:
            self.warning(f"Identificador demasiado largo: {result[:32]}...")
        
        token_type = self.keywords.get(result.lower(), TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, start_column)
    
    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)
            
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)
            
            if self.current_char == '/':
                self.advance()
                if self.current_char == '/' or self.current_char == '*':
                    self.skip_comment()
                    continue
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUALS, '==', self.line, self.column - 2)
                return Token(TokenType.ASSIGN, '=', self.line, self.column - 1)
            
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUALS, '>=', self.line, self.column - 2)
                return Token(TokenType.GREATER_THAN, '>', self.line, self.column - 1)
            
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUALS, '<=', self.line, self.column - 2)
                return Token(TokenType.LESS_THAN, '<', self.line, self.column - 1)
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column - 1)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column - 1)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column - 1)
            
            if self.current_char == '"':
                return self.string()
            
            self.error(f"Carácter no reconocido: '{self.current_char}'")
        
        return Token(TokenType.EOF, None, self.line, self.column) 