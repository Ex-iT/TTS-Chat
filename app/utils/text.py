import re

def strip_markdown(text: str) -> str:
    """
    Remove common markdown styling so it isn't read aloud by TTS.
    """
    # 1. Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # 2. Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 3. Remove bold/italic: **outer **inner**** or __outer __inner____
    # We do it a couple of times to handle some nesting
    for _ in range(2):
        text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
        text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    # 4. Remove links: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # 5. Remove headers: # Header
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    # 6. Remove list markers: * item or 1. item
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # 7. Remove blockquotes: > quote
    text = re.sub(r"^\s*>\s+", "", text, flags=re.MULTILINE)
    # 8. Final cleanup: strip extra whitespace
    return text.strip()
