# Copilot Instructions

## General Guidelines
- First general instruction
- Second general instruction

## Code Style
- Use specific formatting rules
- Follow naming conventions

## LazyImport Usage
- When using LazyImport with modules that have multiple classes, prioritize the main/public class during class extraction.
- For `connection_validator.py`, ensure that `ConnectionValidator` is recognized as the main class, even if `CEchoValidator` appears first in inspect results.
- Enhance the `LazyImport._load_class()` method to check for key methods in classes or allow for explicit class selection to improve accuracy in class loading.