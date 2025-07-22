import json
import re
import os
from typing import Optional, List, Dict
from google import genai
from google.genai import types
from bot.helpers.date_util import now_as_string
from bot.constants import (
    GEMINI_API_KEY,
    GEMINI_SYSTEM_INSTRUCTION_BASE,
    GEMINI_SYSTEM_INSTRUCTION_NORMAL,
    GEMINI_SYSTEM_INSTRUCTION_PARSE,
    GEMINI_SYSTEM_INSTRUCTION_VERIFICATION
)


class LLMModel:
    def __init__(self):
        os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
        self.client = genai.Client()

    def create_base_chat_model(self, history: Optional[List] = None):
        return self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_BASE, history)
    
    def create_parse_chat_model(self, history: Optional[List] = None):
        return self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_PARSE.replace('{d}', now_as_string()), history)
    
    def create_chat_model(self, instruction: str, history: Optional[List] = None):
        """Create a chat model with given instruction and history."""
        return self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(system_instruction=instruction),
            history=history
        )
    
    def parse_json_response(self, text: str) -> Dict:
        """Parse JSON from Gemini response, handling code blocks."""
        clean_text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
        return json.loads(clean_text)
    
    def analyze_message_intent(self, message: str) -> Dict:
        """Analyze message intent using base instruction."""
        chat = self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_BASE)
        response = chat.send_message(message)
        return self.parse_json_response(response.text)
    
    def process_transaction(self, message: str, history: Optional[List] = None) -> str:
        """Process transaction message with parsing instruction."""

        instruction = GEMINI_SYSTEM_INSTRUCTION_PARSE.replace('{d}', now_as_string())
        
        chat = self.create_chat_model(instruction, history)
        response = chat.send_message(message)
        return response.text
    
    def handle_normal_conversation(self, message: str, history: Optional[List] = None) -> str:
        """Handle normal conversation."""
        chat = self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_NORMAL, history)
        response = chat.send_message(message)
