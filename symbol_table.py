"""
Symbol table module for tracking variables and their types.
"""
from enum import Enum, auto
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime

class SymbolType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    ARRAY = auto()
    EXPRESSION = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name.capitalize()

@dataclass
class SymbolInfo:
    """Detailed information about a symbol's usage"""
    declared_line: int = 0
    last_modified_line: int = 0
    used_lines: Set[int] = field(default_factory=set)
    last_accessed: datetime = field(default_factory=datetime.now)
    is_initialized: bool = False
    scope_level: int = 0

class Symbol:
    def __init__(self, name: str, value: Any = None, line: int = 0):
        self.name = name
        self.value = value
        self.type = self._infer_type(value)
        self.info = SymbolInfo(declared_line=line)
        self.expression = None  # Para almacenar expresiones complejas

    def _infer_type(self, value: Any) -> SymbolType:
        """Infer the type of a value."""
        if value is None:
            return SymbolType.UNKNOWN
        elif isinstance(value, bool):
            return SymbolType.BOOLEAN
        elif isinstance(value, int):
            return SymbolType.INTEGER
        elif isinstance(value, float):
            return SymbolType.FLOAT
        elif isinstance(value, str):
            # Check if it's a string literal (with quotes) or an expression
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                return SymbolType.STRING
            return SymbolType.EXPRESSION
        elif isinstance(value, (list, tuple)):
            return SymbolType.ARRAY
        else:
            return SymbolType.UNKNOWN

    def update_value(self, value: Any, line: int = 0):
        """Update symbol value and record modification"""
        # Si el valor es una cadena y no es una expresión, eliminar las comillas
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        self.value = value
        self.type = self._infer_type(value)
        self.info.last_modified_line = line
        self.info.is_initialized = True
        self.info.last_accessed = datetime.now()

    def record_usage(self, line: int):
        """Record a usage of this symbol"""
        self.info.used_lines.add(line)
        self.info.last_accessed = datetime.now()

    def set_expression(self, expr: str):
        """Set the expression for complex assignments"""
        self.expression = expr
        self.type = SymbolType.EXPRESSION

    def get_usage_count(self) -> int:
        """Get the number of times this symbol has been used"""
        return len(self.info.used_lines)

    def __str__(self):
        type_str = str(self.type)
        value_str = str(self.value) if self.value is not None else "undefined"
        if self.expression:
            value_str = self.expression
        return f"Symbol(name='{self.name}', type={type_str}, value={value_str})"

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.current_scope: int = 0
        self.scope_stack: List[Set[str]] = [set()]  # Variables en cada nivel de alcance

    def enter_scope(self):
        """Enter a new scope level"""
        self.current_scope += 1
        self.scope_stack.append(set())

    def exit_scope(self):
        """Exit the current scope level"""
        if self.current_scope > 0:
            # Eliminar símbolos del alcance actual
            for var in self.scope_stack[self.current_scope]:
                if var in self.symbols:
                    del self.symbols[var]
            self.scope_stack.pop()
            self.current_scope -= 1

    def insert(self, name: str, value: Any = None, line: int = 0) -> Symbol:
        """Insert a new symbol into the table."""
        if name in self.symbols:
            # Si el símbolo ya existe, actualizar su valor y línea
            symbol = self.symbols[name]
            symbol.update_value(value, line)
        else:
            # Crear un nuevo símbolo
            symbol = Symbol(name, value, line)
            self.symbols[name] = symbol
        return symbol

    def lookup(self, name: str, record_usage: bool = False, line: int = 0) -> Optional[Symbol]:
        """Look up a symbol in the table."""
        symbol = self.symbols.get(name)
        if symbol and record_usage:
            symbol.record_usage(line)
        return symbol

    def update(self, name: str, value: Any, line: int = 0) -> bool:
        """Update the value of an existing symbol."""
        if name in self.symbols:
            self.symbols[name].update_value(value, line)
            return True
        return False

    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols in the table."""
        return self.symbols

    def get_uninitialized_variables(self) -> List[str]:
        """Get a list of all uninitialized variables."""
        return [name for name, symbol in self.symbols.items() 
                if not symbol.info.is_initialized]

    def get_unused_variables(self) -> List[str]:
        """Get a list of all unused variables."""
        return [name for name, symbol in self.symbols.items() 
                if not symbol.info.used_lines]

    def get_symbol_usage(self, name: str) -> Optional[SymbolInfo]:
        """Get usage information for a symbol."""
        symbol = self.symbols.get(name)
        return symbol.info if symbol else None 