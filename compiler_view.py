"""
UI components for the compiler interface.
"""
import flet as ft
from compiler.lexer import Lexer, TokenType
from compiler.parser import Parser
from compiler.symbol_table import SymbolTable
from compiler.intermediate_code import IntermediateCodeGenerator
from .syntax_highlighter import SyntaxHighlighter
from .code_viewer import CodeViewer
from .token_viewer import TokenViewer

class CompilerView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_ui()
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the editor."""
        def handle_keyboard(e: ft.KeyboardEvent):
            if e.key == "F5":  # Compilar con F5
                self.compile_code(None)
            elif e.key == "Tab" and e.shift:  # Shift+Tab para reducir indentación
                self.unindent_line()
            elif e.key == "Tab":  # Tab para indentar
                self.indent_line()
            
        self.page.on_keyboard_event = handle_keyboard
    
    def setup_ui(self):
        """Initialize all UI components."""
        # Line numbers container
        self.line_numbers = ft.Column(
            width=40,
            scroll=ft.ScrollMode.ALWAYS,
            spacing=0,
            controls=[
                ft.Container(
                    content=ft.Text(str(i+1), size=14, color=ft.colors.GREY_400),
                    padding=ft.padding.only(right=5),
                    alignment=ft.alignment.center_right,
                    height=20  # Altura fija para cada línea
                )
                for i in range(15)  # Initial 15 lines
            ]
        )
        
        # Code editor with syntax highlighting
        self.code_editor = ft.TextField(
            multiline=True,
            min_lines=15,
            max_lines=15,
            value="",  # Empezar con editor vacío
            label="Código fuente",
            width=760,  # Reducido para dar espacio a los números de línea
            height=300,  # Altura fija
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),  # Fondo semi-transparente
            border_color=ft.colors.with_opacity(0.4, ft.colors.ON_SURFACE),
            focused_border_color=ft.colors.BLUE,
            cursor_color=ft.colors.WHITE,
            text_style=ft.TextStyle(
                font_family="Consolas",
                size=14,  # Tamaño de fuente ajustado
                weight=ft.FontWeight.NORMAL,
                color=ft.colors.WHITE  # Texto visible
            ),
            on_change=self.on_code_change,
        )
        
        # Syntax highlighting overlay
        self.highlight_container = ft.Container(
            content=None,
            width=760,
            height=300,  # Altura fija igual al editor
            padding=ft.padding.only(left=12, top=48),
            alignment=ft.alignment.top_left,
            expand=True,
            bgcolor=ft.colors.TRANSPARENT,
            visible=False  # Inicialmente oculto
        )
        
        # Editor toolbar
        editor_toolbar = ft.Row([
            ft.Text(
                "Editor de Código",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLUE
            ),
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.CLEANING_SERVICES,
                    tooltip="Limpiar editor",
                    on_click=self.clear_code
                ),
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Restaurar código de ejemplo",
                    on_click=self.reset_code
                ),
                ft.IconButton(
                    icon=ft.icons.FORMAT_INDENT_INCREASE,
                    tooltip="Formatear código",
                    on_click=self.format_code
                ),
                ft.IconButton(
                    icon=ft.icons.HELP_OUTLINE,
                    tooltip="Ayuda",
                    on_click=self.show_help
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Code editor container with line numbers
        code_editor_row = ft.Row([
            self.line_numbers,
            ft.Container(
                content=self.code_editor,
                bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                border_radius=5,
                padding=5,
                height=300  # Altura fija
            )
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)
        
        code_editor_container = ft.Container(
            content=ft.Column([
                editor_toolbar,
                code_editor_row
            ]),
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            border_radius=10,
            padding=10,
            margin=ft.margin.only(bottom=20)
        )
        
        # Output containers using ListView for scrolling
        self.token_container = ft.ListView(
            height=300,
            width=800,
            spacing=2,
            padding=20,
            expand=1
        )
        
        self.symbol_table_container = ft.ListView(
            height=200,
            width=800,
            spacing=2,
            padding=20,
            expand=1
        )
        
        self.intermediate_code_container = ft.ListView(
            height=200,
            width=800,
            spacing=2,
            padding=20,
            expand=1
        )
        
        # Error display
        self.error_text = ft.Text("", color=ft.colors.RED)
        
        # Compile button with loading state
        self.compile_button = ft.ElevatedButton(
            text="Compilar (F5)",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.compile_code,
            width=200,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
                padding=15
            )
        )
        
        # Create main content column with scroll
        main_content = ft.ListView(
            controls=[
                ft.Text("Mini Compilador", size=30, weight=ft.FontWeight.BOLD),
                code_editor_container,
                ft.Row([
                    self.compile_button,
                    self.error_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("Análisis Léxico", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.token_container,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10
                ),
                ft.Text("Tabla de Símbolos", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.symbol_table_container,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10
                ),
                ft.Text("Código Intermedio", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.intermediate_code_container,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10
                ),
            ],
            spacing=20,
            height=800,
            width=850,
            expand=True
        )
        
        # Add the main content directly to the page
        self.page.add(main_content)
    
    def on_code_change(self, e):
        """Handle code changes in the editor."""
        # Update line numbers
        text = self.code_editor.value or ""
        num_lines = text.count('\n') + 1
        current_lines = len(self.line_numbers.controls)
        
        if num_lines > current_lines:
            # Add more line numbers
            for i in range(current_lines, num_lines):
                self.line_numbers.controls.append(
                    ft.Container(
                        content=ft.Text(str(i+1), size=14, color=ft.colors.GREY_400),
                        padding=ft.padding.only(right=5),
                        alignment=ft.alignment.center_right,
                        height=20  # Altura fija para cada línea
                    )
                )
        elif num_lines < current_lines:
            # Remove excess line numbers
            self.line_numbers.controls = self.line_numbers.controls[:num_lines]
        
        # Update syntax highlighting
        self.highlight_syntax(e)
        self.page.update()
    
    def highlight_syntax(self, e):
        """Update syntax highlighting in the code editor."""
        text = self.code_editor.value or ""
        if text:
            highlighted = SyntaxHighlighter.highlight_text(text)
            self.highlight_container.content = highlighted
            self.highlight_container.visible = True
        else:
            self.highlight_container.visible = False
        self.page.update()
    
    def indent_line(self):
        """Indent the current line or selected text."""
        if not self.code_editor.value:
            return
        
        # Get cursor position and text
        text = self.code_editor.value
        selection_start = self.code_editor.selection.start
        selection_end = self.code_editor.selection.end
        
        # If there's no selection, indent current line
        if selection_start == selection_end:
            lines = text.split('\n')
            current_line = text.count('\n', 0, selection_start)
            lines[current_line] = "    " + lines[current_line]
            self.code_editor.value = '\n'.join(lines)
        else:
            # Indent selected lines
            selected_text = text[selection_start:selection_end]
            indented_text = "    " + selected_text.replace('\n', '\n    ')
            self.code_editor.value = text[:selection_start] + indented_text + text[selection_end:]
        
        self.highlight_syntax(None)
    
    def unindent_line(self):
        """Remove indentation from the current line or selected text."""
        if not self.code_editor.value:
            return
        
        # Get cursor position and text
        text = self.code_editor.value
        selection_start = self.code_editor.selection.start
        selection_end = self.code_editor.selection.end
        
        # If there's no selection, unindent current line
        if selection_start == selection_end:
            lines = text.split('\n')
            current_line = text.count('\n', 0, selection_start)
            if lines[current_line].startswith('    '):
                lines[current_line] = lines[current_line][4:]
            elif lines[current_line].startswith('\t'):
                lines[current_line] = lines[current_line][1:]
            self.code_editor.value = '\n'.join(lines)
        else:
            # Unindent selected lines
            selected_text = text[selection_start:selection_end]
            lines = selected_text.split('\n')
            unindented_lines = []
            for line in lines:
                if line.startswith('    '):
                    unindented_lines.append(line[4:])
                elif line.startswith('\t'):
                    unindented_lines.append(line[1:])
                else:
                    unindented_lines.append(line)
            self.code_editor.value = text[:selection_start] + '\n'.join(unindented_lines) + text[selection_end:]
        
        self.highlight_syntax(None)
    
    def clear_code(self, e):
        """Clear the code editor."""
        self.code_editor.value = ""
        self.highlight_syntax(None)
        self.page.update()
    
    def show_help(self, e):
        """Show help dialog with keyboard shortcuts and usage information."""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        help_dialog = ft.AlertDialog(
            title=ft.Text("Ayuda del Editor"),
            content=ft.Column(
                controls=[
                    ft.Text("Atajos de teclado:", weight=ft.FontWeight.BOLD),
                    ft.Text("• F5: Compilar código"),
                    ft.Text("• Tab: Indentar línea o selección"),
                    ft.Text("• Shift+Tab: Reducir indentación"),
                    ft.Divider(),
                    ft.Text("Estructura básica del programa:", weight=ft.FontWeight.BOLD),
                    ft.Text("""program
var x;
var y;
x = 5;
y = x + 3 * 2;""")
                ],
                tight=True
            ),
            actions=[
                ft.TextButton(text="Cerrar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = help_dialog
        self.page.dialog.open = True
        self.page.update()
    
    def compile_code(self, e):
        """Handle the compilation process."""
        # Clear previous results
        self.error_text.value = ""
        self.token_container.controls.clear()
        self.symbol_table_container.controls.clear()
        self.intermediate_code_container.controls.clear()
        
        if not self.code_editor.value.strip():
            self.error_text.value = "Error: El código está vacío"
            self.error_text.color = ft.colors.RED
            self.page.update()
            return
        
        # Disable compile button during compilation
        self.compile_button.disabled = True
        self.page.update()
        
        try:
            # Análisis de líneas antes de la compilación
            lines = self.code_editor.value.split('\n')
            warnings = []
            
            for i, line in enumerate(lines, 1):
                # Verificar líneas vacías o solo con espacios
                if not line.strip():
                    warnings.append(f"Línea {i}: Está vacía")
                
                # Verificar indentación
                if line.startswith(' ') and not line.startswith('    '):
                    warnings.append(f"Línea {i}: Tiene indentación incorrecta")
                
                # Verificar longitud de línea
                if len(line) > 80:
                    warnings.append(f"Línea {i}: Es muy larga (más de 80 caracteres)")
            
            # Mostrar advertencias si las hay
            if warnings:
                self.error_text.value = "Advertencias:\n" + "\n".join(warnings)
                self.error_text.color = ft.colors.ORANGE
                self.page.update()
            
            # Lexical analysis
            lexer = Lexer(self.code_editor.value)
            tokens = []
            token = lexer.get_next_token()
            
            while token.type != TokenType.EOF:
                tokens.append(token)
                token = lexer.get_next_token()
            
            # Create token view
            token_view = TokenViewer.create_token_view(tokens)
            if isinstance(token_view, ft.Control):
                self.token_container.controls.append(token_view)
            elif isinstance(token_view, list):
                self.token_container.controls.extend(token_view)
            
            # Reset lexer for parser
            lexer = Lexer(self.code_editor.value)
            symbol_table = SymbolTable()
            
            # Parsing
            parser = Parser(lexer, symbol_table)
            ast = parser.parse()
            
            # Symbol table view
            symbols = symbol_table.get_all_symbols()
            if not symbols:
                self.symbol_table_container.controls.append(
                    ft.Text("No hay símbolos en la tabla.", color=ft.colors.GREY_400)
                )
            else:
                symbol_view = CodeViewer.create_symbol_table_view(symbols)
                self.symbol_table_container.controls.append(symbol_view)
            
            # Intermediate code generation
            code_gen = IntermediateCodeGenerator()
            code_gen.generate(ast)
            
            # Intermediate code view
            code = code_gen.get_code()
            if not code:
                self.intermediate_code_container.controls.append(
                    ft.Text("No hay código intermedio generado.", color=ft.colors.GREY_400)
                )
            else:
                # Crear una vista más detallada del código intermedio
                code_view = CodeViewer.create_intermediate_code_view(code)
                if isinstance(code_view, ft.Control):
                    self.intermediate_code_container.controls.append(code_view)
                elif isinstance(code_view, list):
                    self.intermediate_code_container.controls.extend(code_view)
            
            # Si no hay advertencias, mostrar éxito
            if not warnings:
                self.error_text.value = "Compilación exitosa"
                self.error_text.color = ft.colors.GREEN
            
        except Exception as error:
            self.error_text.value = f"Error: {str(error)}"
            self.error_text.color = ft.colors.RED
        
        finally:
            # Re-enable compile button
            self.compile_button.disabled = False
            self.page.update()
    
    def reset_code(self, e):
        """Reset the code editor to the default example."""
        self.code_editor.value = """program
var x = 5;
var y = 7;

// Ejemplo de if
if (x > 5) {
    y = 10;
} else {
    y = 0;
}

// Ejemplo de while
while (x > 0) {
    y = y + 1;
    x = x - 1;
}"""
        
        # Actualizar números de línea
        text = self.code_editor.value
        num_lines = text.count('\n') + 1
        self.line_numbers.controls = [
            ft.Container(
                content=ft.Text(str(i+1), size=14, color=ft.colors.GREY_400),
                padding=ft.padding.only(right=5),
                alignment=ft.alignment.center_right,
                height=20  # Altura fija para cada línea
            )
            for i in range(num_lines)
        ]
        
        self.highlight_syntax(None)
        self.page.update()
    
    def format_code(self, e):
        """Format the code with proper indentation."""
        if not self.code_editor.value:
            return
            
        lines = self.code_editor.value.split("\n")
        indent_level = 0
        formatted_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:  # Si la línea no está vacía
                # Reducir la indentación para líneas que cierran un bloque
                if stripped_line.startswith("}"):
                    indent_level = max(0, indent_level - 1)
                
                # Añadir la línea con la indentación correcta
                formatted_lines.append("    " * indent_level + stripped_line)
                
                # Aumentar la indentación después de abrir un bloque
                if stripped_line.endswith("{"):
                    indent_level += 1
            else:
                formatted_lines.append("")  # Mantener líneas vacías
        
        self.code_editor.value = "\n".join(formatted_lines)
        self.highlight_syntax(None)
        self.page.update() 