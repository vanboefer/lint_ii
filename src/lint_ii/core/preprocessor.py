import mistune
import re


def extract_text_from_node(node: dict | str) -> str:
    """Recursively extract all text from a node."""
    if isinstance(node, dict):
        if node.get('type') == 'text':
            return node.get('raw', '')
        if 'children' in node:
            return ' '.join(extract_text_from_node(child) for child in node['children'])
    return ''


def fix_quotemarks(text) -> str:
    """Replace 'weird' quotemarks (e.g. curly) with straight double quotemarks."""
    quotemarks = [i for i in "«»‘’‛“”„‟‹›"]
    for quotemark in quotemarks:
        text = text.replace(quotemark, '"')
    return text


def preprocess_text(text: str) -> str:
    """Extract text from paragraphs, blockquotes, and lists. Remove redundant whitespaces."""
    markdown = mistune.create_markdown(renderer='ast')
    nodes: list[dict] = markdown(text)  # type: ignore
    paragraphs = []

    for node in nodes:
        if node['type'] in ['paragraph', 'block_quote', 'list']:
            paragraph = extract_text_from_node(node)
            if ' ' in paragraph:  # filter out one word sentences
                paragraphs.append(paragraph)

    combined_text = ' '.join(paragraphs)
    regex = re.compile(r'\s+')

    clean_text, _ = regex.subn(' ', combined_text)
    clean_text_without_quotemarks = fix_quotemarks(clean_text)
    return clean_text_without_quotemarks
