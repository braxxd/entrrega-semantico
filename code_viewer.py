"""
Enhanced code viewer components.
"""
import flet as ft
from compiler.intermediate_code import ThreeAddressCode
from compiler.symbol_table import Symbol, SymbolType

class CodeViewer:
    @staticmethod
    def create_intermediate_code_view(instructions: list[ThreeAddressCode]) -> ft.Column:
        """Create a structured view of the intermediate code."""
        # Crear tabla de código intermedio
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Línea")),
                ft.DataColumn(ft.Text("Operación")),
                ft.DataColumn(ft.Text("Arg1")),
                ft.DataColumn(ft.Text("Arg2")),
                ft.DataColumn(ft.Text("Resultado")),
                ft.DataColumn(ft.Text("Comentario")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i + 1))),
                        ft.DataCell(ft.Container(
                            content=ft.Text(str(instr.op)),
                            padding=5,
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLUE) if instr.op in {'+', '-', '*', '/', 'ADD', 'SUB', 'MUL', 'DIV', 'GT', 'LT', 'EQ', 'CMP', 'JZ', 'JMP', 'LABEL'} else None
                        )),
                        ft.DataCell(ft.Text(
                            str(instr.arg1 if instr.arg1 is not None else ""),
                            color=ft.colors.GREEN if CodeViewer._is_constant(instr.arg1) else 
                                  ft.colors.PURPLE if instr.op == 'LABEL' else None,
                            weight=ft.FontWeight.BOLD if instr.op == 'LABEL' else None
                        )),
                        ft.DataCell(ft.Text(
                            str(instr.arg2 if instr.arg2 is not None else ""),
                            color=ft.colors.GREEN if CodeViewer._is_constant(instr.arg2) else 
                                  ft.colors.RED if instr.op in {'JZ', 'JMP'} else None
                        )),
                        ft.DataCell(ft.Text(
                            str(instr.result if instr.result is not None else ""),
                            color=ft.colors.BLUE if instr.result and instr.result.startswith('t') else None
                        )),
                        ft.DataCell(ft.Text(
                            instr.comment if hasattr(instr, 'comment') else "",
                            color=ft.colors.GREY_400,
                            italic=True
                        )),
                    ]
                )
                for i, instr in enumerate(instructions)
            ],
        )
        
        # Agregar estadísticas del código intermedio
        stats = CodeViewer._generate_intermediate_code_stats(instructions)
        
        # Crear vista de estadísticas
        stats_view = ft.Container(
            content=ft.Column([
                ft.Text("Estadísticas del código intermedio:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"Variables temporales: {stats['temp_vars']}"),
                ft.Text(f"Operaciones aritméticas: {stats['arithmetic_ops']}"),
                ft.Text(f"Asignaciones: {stats['assignments']}"),
                ft.Text(f"Operaciones de control: {stats['control_ops']}"),
                ft.Text(f"Constantes únicas: {stats['constants']}"),
            ]),
            padding=10,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLUE_GREY),
            border_radius=5,
        )
        
        return ft.Column([
            ft.Text("Código Intermedio:", size=20, weight=ft.FontWeight.BOLD),
            table,
            ft.Divider(),
            stats_view,
        ])
    
    @staticmethod
    def _is_constant(value: str) -> bool:
        """Check if a value represents a constant."""
        if not value:
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return value.startswith('"') and value.endswith('"')
    
    @staticmethod
    def _generate_intermediate_code_stats(instructions: list[ThreeAddressCode]) -> dict:
        """Generate statistics for the intermediate code."""
        stats = {
            'temp_vars': 0,
            'arithmetic_ops': 0,
            'assignments': 0,
            'control_ops': 0,
            'constants': set()
        }
        
        for instr in instructions:
            # Contar variables temporales
            if instr.result and instr.result.startswith('t'):
                stats['temp_vars'] += 1
            
            # Contar operaciones aritméticas
            if instr.op in {'+', '-', '*', '/', 'ADD', 'SUB', 'MUL', 'DIV', 'GT', 'LT', 'EQ'}:
                stats['arithmetic_ops'] += 1
            
            # Contar asignaciones
            if instr.op in {':=', 'ASSIGN'}:
                stats['assignments'] += 1
            
            # Contar operaciones de control
            if instr.op in {'JZ', 'JMP', 'LABEL', 'CMP'}:
                stats['control_ops'] += 1
            
            # Contar constantes únicas
            if CodeViewer._is_constant(instr.arg1):
                stats['constants'].add(instr.arg1)
            if CodeViewer._is_constant(instr.arg2):
                stats['constants'].add(instr.arg2)
        
        stats['constants'] = len(stats['constants'])
        return stats

    @staticmethod
    def create_symbol_table_view(symbols: dict) -> ft.Column:
        """Create a structured view of the symbol table."""
        if not symbols:
            return ft.Column(controls=[ft.Text("No hay símbolos en la tabla.", color=ft.colors.GREY_400)])
        
        # Convertir los símbolos a una lista ordenada por nombre
        symbol_list = [(name, symbol) for name, symbol in symbols.items()]
        symbol_list.sort(key=lambda x: x[0])
        
        # Crear la tabla principal de símbolos
        main_table = ft.DataTable(
            width=750,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor/Expresión", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Línea Dec.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Última Mod.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Alcance", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        # Nombre de la variable
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                name,
                                color=ft.colors.BLUE,
                                weight=ft.FontWeight.BOLD
                            ),
                            padding=5
                        )),
                        # Tipo de la variable
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                str(symbol.type),
                                color=ft.colors.GREEN
                            ),
                            padding=5
                        )),
                        # Valor actual o expresión
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                str(symbol.expression if symbol.expression else 
                                    (symbol.value if symbol.value is not None else "undefined")),
                                color=ft.colors.ORANGE,
                                no_wrap=True,
                                overflow="ellipsis"
                            ),
                            padding=5,
                            tooltip=str(symbol.expression if symbol.expression else 
                                      (symbol.value if symbol.value is not None else "undefined"))
                        )),
                        # Estado con detalles
                        ft.DataCell(ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        name=ft.icons.CHECK_CIRCLE if symbol.info.is_initialized 
                                             else ft.icons.ERROR,
                                        color=ft.colors.GREEN if symbol.info.is_initialized 
                                              else ft.colors.RED,
                                        size=16
                                    ),
                                    ft.Text(
                                        "Inicializado" if symbol.info.is_initialized 
                                        else "No inicializado",
                                        color=ft.colors.GREEN if symbol.info.is_initialized 
                                              else ft.colors.RED
                                    )
                                ],
                                spacing=2
                            ),
                            padding=5
                        )),
                        # Línea de declaración
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                str(symbol.info.declared_line),
                                color=ft.colors.BLUE_GREY
                            ),
                            padding=5
                        )),
                        # Última modificación
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                str(symbol.info.last_modified_line if symbol.info.last_modified_line > 0 
                                    else "-"),
                                color=ft.colors.BLUE_GREY
                            ),
                            padding=5
                        )),
                        # Usos con detalles
                        ft.DataCell(ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text(
                                        str(len(symbol.info.used_lines)),
                                        color=ft.colors.PURPLE
                                    ),
                                    ft.Icon(
                                        name=ft.icons.WARNING if not symbol.info.used_lines 
                                             else ft.icons.CHECK,
                                        color=ft.colors.ORANGE if not symbol.info.used_lines 
                                              else ft.colors.GREEN,
                                        size=16
                                    )
                                ],
                                spacing=2
                            ),
                            padding=5,
                            tooltip=f"Líneas: {', '.join(map(str, sorted(symbol.info.used_lines)))}" 
                                   if symbol.info.used_lines else "No utilizada"
                        )),
                        # Nivel de alcance
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                f"Nivel {symbol.info.scope_level}",
                                color=ft.colors.BLUE_GREY
                            ),
                            padding=5
                        )),
                    ]
                )
                for name, symbol in symbol_list
            ]
        )

        # Estadísticas de la tabla de símbolos
        stats = {
            'total': len(symbols),
            'uninitialized': sum(1 for _, s in symbol_list if not s.info.is_initialized),
            'unused': sum(1 for _, s in symbol_list if not s.info.used_lines)
        }

        stats_container = ft.Container(
            content=ft.Column([
                ft.Text("Estadísticas de la Tabla de Símbolos:", 
                       size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(f"Total de símbolos: {stats['total']}", 
                           color=ft.colors.BLUE),
                    ft.VerticalDivider(),
                    ft.Text(f"No inicializados: {stats['uninitialized']}", 
                           color=ft.colors.RED),
                    ft.VerticalDivider(),
                    ft.Text(f"No utilizados: {stats['unused']}", 
                           color=ft.colors.ORANGE)
                ])
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(bottom=10)
        )

        return ft.Column(
            controls=[
                stats_container,
                main_table
            ],
            scroll=ft.ScrollMode.AUTO
        ) 