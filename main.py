"""
Main entry point for the mini compiler application.
"""
import flet as ft
from ui.compiler_view import CompilerView

def main(page: ft.Page):
    """Initialize the application."""
    page.title = "Mini Compilador"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Create the main view
    CompilerView(page)

if __name__ == "__main__":
    ft.app(target=main) 