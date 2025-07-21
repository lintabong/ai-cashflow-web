from typing import List, Optional, Dict
from google.genai import types

def build_history_from_memory(memory_cache, user_id: str) -> Optional[List]:
    """Build conversation history from memory cache."""
    history = []
    context = memory_cache.get_context(user_id)
    
    if context and 'messages' in context and len(context['messages']) >= 2:
        for message in context['messages']:
            content = types.Content(
                role=message['role'], 
                parts=[types.Part.from_text(text=message['text'])]
            )
            history.append(content)
    
    return history if history else None
