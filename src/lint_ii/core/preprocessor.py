"""Text Preprocessing Utilities

This module provides functions for preprocessing and cleaning text extracted from 
Markdown documents; it also works for plain text. 

It handles text extraction from Markdown AST nodes, quotemark normalization, and whitespace cleanup.

Functions
---------
extract_text_from_node(node: dict | str) -> str
    Recursively extracts all text content from a Markdown AST node and its children.

fix_quotemarks(text: str) -> str
    Normalizes various quotemark styles (curly quotes, guillemets, etc.) to 
    straight double quotes.

preprocess_text(text: str) -> str
    Main preprocessing function that extracts text from Markdown, normalizes 
    quotemarks, and removes redundant whitespace.

Notes
-----
- Only text from paragraphs, blockquotes, and lists is extracted; other Markdown elements (headers, code blocks, etc.) are ignored.
- All quotemark variants are converted to ASCII double quotes (").
- Multiple consecutive whitespace characters are collapsed to a single space.
"""

import mistune
import re


def extract_text_from_node(node: dict | str) -> str:
    """Recursively extract all text from a Markdown AST node and its children."""
    if isinstance(node, dict):
        if node.get('type') == 'text':
            return node.get('raw', '')
        if 'children' in node:
            return ' '.join(extract_text_from_node(child) for child in node['children'])
    return ''


def fix_quotemarks(text) -> str:
    """
    Normalizes various quotemark styles (curly quotes, guillemets, etc.) to straight double quotes.
    """
    quotemarks = [i for i in "«»‘’‛“”„‟‹›"]
    for quotemark in quotemarks:
        text = text.replace(quotemark, '"')
    return text


def preprocess_text(text: str) -> str:
    """
    Main preprocessing function that extracts text from Markdown, normalizes quotemarks, and removes redundant whitespace.
    """
    markdown = mistune.create_markdown(renderer='ast')
    nodes: list[dict] = markdown(text)  # type: ignore
    paragraphs = []

    for node in nodes:
        if node['type'] in ['paragraph', 'block_quote', 'list']:
            paragraph = extract_text_from_node(node)
            paragraphs.append(paragraph)

    combined_text = ' '.join(paragraphs)
    regex = re.compile(r'\s+')

    clean_text, _ = regex.subn(' ', combined_text)
    clean_text_without_quotemarks = fix_quotemarks(clean_text)
    return clean_text_without_quotemarks
