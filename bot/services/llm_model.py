import json
import re
import os
from typing import Optional, List, Dict
from google import genai
from google.genai import types
from bot.helpers.date_util import now_as_string
from bot.constants import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_SYSTEM_INSTRUCTION_BASE,
    GEMINI_SYSTEM_INSTRUCTION_BASE_PHOTO
)


class LLMModel:
    def __init__(self):
        os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
        self.client = genai.Client()

    def create_base_chat_model(self, history: Optional[List] = None):
        return self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_BASE.replace('{d}', now_as_string()), history)

    def create_chat_model(self, instruction: str, history: Optional[List] = None):
        return self.client.chats.create(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(system_instruction=instruction),
            history=history
        )

    def parse_context_image(self, image_bytes):
        return self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            GEMINI_SYSTEM_INSTRUCTION_BASE_PHOTO
            ]
        )

    def parse_json_response(self, text: str) -> Dict:
        clean_text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
        return json.loads(clean_text)
