
import re
import json

def parse_json(text):
    """Parse JSON from Gemini response, handling code blocks."""
    clean_text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
    return json.loads(clean_text)

def markdown_to_html(text: str) -> str:
    # Bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Inline code `text`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text
