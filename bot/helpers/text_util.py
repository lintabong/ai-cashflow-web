

import re
import json

def parse_json(text):
    """Parse JSON from Gemini response, handling code blocks."""
    clean_text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
    return json.loads(clean_text)
