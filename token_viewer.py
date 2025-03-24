"""
Token viewer component for displaying lexical analysis results.
"""
import flet as ft
from compiler.lexer import Token, TokenType

class TokenViewer:
    TOKEN_CATEGORIES = {
        "Palabras Clave": [
            TokenType.PROGRAM, TokenType.VAR, TokenType.INT, TokenType.FLOAT,
            TokenType.STRING, TokenType.IF, TokenType.ELSE, TokenType.WHILE,
            TokenType.FOR, TokenType.DO, TokenType.FUNCTION, TokenType.RETURN,
            TokenType.PRINT
        ],
        "Tipos de Datos": [
            TokenType.INTEGER_CONST, TokenType.FLOAT_CONST, TokenType.STRING_LITERAL,
            TokenType.BOOL, TokenType.TRUE, TokenType.FALSE
        ],
        "Operadores": [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.ASSIGN
        ],
        "Comparación": [
            TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN,
            TokenType.GREATER_THAN, TokenType.LESS_EQUALS, TokenType.GREATER_EQUALS
        ],
        "Lógicos": [
            TokenType.AND, TokenType.OR, TokenType.NOT
        ],
        "Delimitadores": [
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMICOLON,
            TokenType.COMMA, TokenType.DOT, TokenType.COLON
        ],
        "Otros": [
            TokenType.IDENTIFIER, TokenType.COMMENT, TokenType.EOF, TokenType.ERROR
        ]
    }

    TOKEN_COLORS = {
        "Palabras Clave": "#569CD6",      # Azul
        "Tipos de Datos": "#B5CEA8",      # Verde claro
        "Operadores": "#D4D4D4",          # Gris claro
        "Comparación": "#C586C0",         # Morado
        "Lógicos": "#569CD6",             # Azul
        "Delimitadores": "#808080",       # Gris
        "Otros": "#CE9178",               # Naranja
        "Error": "#F44747"                # Rojo
    }

    @staticmethod
    def get_token_category(token_type: TokenType) -> str:
        """Obtiene la categoría de un tipo de token."""
        for category, types in TokenViewer.TOKEN_CATEGORIES.items():
            if token_type in types:
                return category
        return "Otros"

    @staticmethod
    def create_token_view(tokens: list[Token]) -> ft.Column:
        """Crea una vista estructurada de tokens con categorías y estadísticas."""
        # Agrupar tokens por categoría
        tokens_by_category = {}
        for token in tokens:
            category = TokenViewer.get_token_category(token.type)
            if category not in tokens_by_category:
                tokens_by_category[category] = []
            tokens_by_category[category].append(token)

        # Crear estadísticas
        total_tokens = len(tokens)
        stats_text = [
            ft.Text("Estadísticas del Análisis Léxico:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"Total de tokens: {total_tokens}"),
        ]
        
        for category, cat_tokens in tokens_by_category.items():
            percentage = (len(cat_tokens) / total_tokens) * 100 if total_tokens > 0 else 0
            stats_text.append(
                ft.Text(f"{category}: {len(cat_tokens)} ({percentage:.1f}%)")
            )

        # Crear lista de tokens por categoría
        token_lists = []
        for category, cat_tokens in tokens_by_category.items():
            color = TokenViewer.TOKEN_COLORS.get(category, "#FFFFFF")
            
            category_tokens = ft.Column(
                controls=[
                    ft.Text(category, size=14, weight=ft.FontWeight.BOLD),
                    *[TokenViewer._create_token_item(token, color) for token in cat_tokens]
                ],
                spacing=2
            )
            
            token_lists.append(category_tokens)

        # Combinar estadísticas y listas de tokens
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(controls=stats_text),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=5,
                    margin=ft.margin.only(bottom=10)
                ),
                ft.Row(
                    controls=token_lists,
                    scroll=ft.ScrollMode.ALWAYS,
                    spacing=20
                )
            ],
            scroll=ft.ScrollMode.ALWAYS
        )

    @staticmethod
    def _create_token_item(token: Token, color: str) -> ft.Container:
        """Crea una representación visual de un token individual."""
        if token.type == TokenType.ERROR:
            color = TokenViewer.TOKEN_COLORS["Error"]
        
        token_info = [
            ft.Text(
                f"Tipo: {token.type.to_spanish()}",
                color=color,
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(f"Valor: '{token.value}'"),
            ft.Text(f"Línea: {token.line}, Columna: {token.column}")
        ]
        
        if token.error_message:
            token_info.append(
                ft.Text(f"Error: {token.error_message}", color=TokenViewer.TOKEN_COLORS["Error"])
            )
        
        return ft.Container(
            content=ft.Column(token_info),
            border=ft.border.all(1, color),
            border_radius=5,
            padding=5,
            margin=2
        ) 