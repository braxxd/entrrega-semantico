"""
Syntax highlighting for the code editor.
"""
import flet as ft
from compiler.lexer import Lexer, TokenType

class SyntaxHighlighter:
    # Color schemes for different token types
    COLORS = {
        # Keywords
        TokenType.PROGRAM: ft.colors.BLUE,
        TokenType.VAR: ft.colors.BLUE,
        TokenType.IF: ft.colors.BLUE,
        TokenType.ELSE: ft.colors.BLUE,
        TokenType.WHILE: ft.colors.BLUE,
        TokenType.FOR: ft.colors.BLUE,
        TokenType.DO: ft.colors.BLUE,
        TokenType.FUNCTION: ft.colors.BLUE,
        TokenType.RETURN: ft.colors.BLUE,
        
        # Data Types
        TokenType.INT: ft.colors.TEAL,
        TokenType.FLOAT: ft.colors.TEAL,
        TokenType.STRING: ft.colors.TEAL,
        TokenType.BOOL: ft.colors.TEAL,
        
        # Literals
        TokenType.INTEGER_CONST: ft.colors.ORANGE,
        TokenType.FLOAT_CONST: ft.colors.ORANGE,
        TokenType.STRING_LITERAL: ft.colors.GREEN,
        TokenType.TRUE: ft.colors.PURPLE,
        TokenType.FALSE: ft.colors.PURPLE,
        
        # Operators
        TokenType.PLUS: ft.colors.RED,
        TokenType.MINUS: ft.colors.RED,
        TokenType.MULTIPLY: ft.colors.RED,
        TokenType.DIVIDE: ft.colors.RED,
        TokenType.MODULO: ft.colors.RED,
        TokenType.ASSIGN: ft.colors.RED,
        
        # Comparison Operators
        TokenType.EQUALS: ft.colors.RED,
        TokenType.NOT_EQUALS: ft.colors.RED,
        TokenType.LESS_THAN: ft.colors.RED,
        TokenType.GREATER_THAN: ft.colors.RED,
        TokenType.LESS_EQUALS: ft.colors.RED,
        TokenType.GREATER_EQUALS: ft.colors.RED,
        
        # Logical Operators
        TokenType.AND: ft.colors.BLUE,
        TokenType.OR: ft.colors.BLUE,
        TokenType.NOT: ft.colors.BLUE,
        
        # Delimiters
        TokenType.LPAREN: ft.colors.GREY,
        TokenType.RPAREN: ft.colors.GREY,
        TokenType.LBRACE: ft.colors.GREY,
        TokenType.RBRACE: ft.colors.GREY,
        TokenType.LBRACKET: ft.colors.GREY,
        TokenType.RBRACKET: ft.colors.GREY,
        TokenType.SEMICOLON: ft.colors.GREY,
        TokenType.COMMA: ft.colors.GREY,
        TokenType.DOT: ft.colors.GREY,
        TokenType.COLON: ft.colors.GREY,
        
        # Comments
        TokenType.COMMENT: ft.colors.GREEN_400,
        
        # Others
        TokenType.IDENTIFIER: ft.colors.WHITE,
        TokenType.ERROR: ft.colors.RED_400,
    }

    @staticmethod
    def highlight_text(text: str) -> ft.Text:
        """Highlight the syntax of the given text."""
        if not text:
            return ft.Text("")
        
        try:
            lexer = Lexer(text)
            spans = []
            current_pos = 0
            
            token = lexer.get_next_token()
            while token.type != TokenType.EOF:
                # Calcular la posición correcta del token
                token_start = current_pos
                token_length = len(str(token.value))
                
                # Crear un TextSpan con el color apropiado
                color = SyntaxHighlighter.COLORS.get(token.type, ft.colors.WHITE)
                
                # Agregar estilo de error si es un token de error
                if token.type == TokenType.ERROR:
                    spans.append(
                        ft.TextSpan(
                            text=str(token.value),
                            style=ft.TextStyle(
                                color=color,
                                font_family="Consolas",
                                bgcolor=ft.colors.with_opacity(0.3, ft.colors.RED),
                                weight=ft.FontWeight.BOLD,
                                size=16
                            )
                        )
                    )
                else:
                    spans.append(
                        ft.TextSpan(
                            text=str(token.value),
                            style=ft.TextStyle(
                                color=color,
                                font_family="Consolas",
                                size=16
                            )
                        )
                    )
                
                # Agregar espacios en blanco entre tokens
                next_pos = lexer.pos
                if next_pos > current_pos + token_length:
                    whitespace = text[current_pos + token_length:next_pos]
                    if whitespace:
                        spans.append(
                            ft.TextSpan(
                                text=whitespace,
                                style=ft.TextStyle(
                                    font_family="Consolas",
                                    size=16,
                                    color=ft.colors.WHITE
                                )
                            )
                        )
                
                current_pos = next_pos
                token = lexer.get_next_token()
            
            # Agregar cualquier texto restante
            if current_pos < len(text):
                spans.append(
                    ft.TextSpan(
                        text=text[current_pos:],
                        style=ft.TextStyle(
                            font_family="Consolas",
                            size=16,
                            color=ft.colors.WHITE
                        )
                    )
                )
            
            return ft.Text(
                spans=spans,
                font_family="Consolas",
                size=16,
                selectable=True,
                color=ft.colors.WHITE,
                bgcolor=ft.colors.TRANSPARENT,
                height=300  # Altura fija igual al editor
            )
            
        except Exception as e:
            return ft.Text(f"Error en el resaltado de sintaxis: {str(e)}", color=ft.colors.RED) 