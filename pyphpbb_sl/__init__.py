"""Top-level package for pyphpbb-sl."""

__author__ = """Sergeileduc"""
__email__ = "sergei.leduc@gmail.com"
__version__ = "0.12.0"


from .phpbb import Message, PhpBB

__all__ = ["PhpBB", "Message"]
