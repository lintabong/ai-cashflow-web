import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google import genai
from google.genai import types

@dataclass
class ChatSession:
    """Data class untuk menyimpan session chat"""
    user_id: str
    history: List[Dict[str, Any]]
    instruction_type: str
    created_at: str
    last_activity: str

class GeminiChatManager:
    def __init__(self, api_key: str):
        """
        Initialize Gemini Chat Manager
        
        Args:
            api_key: Google AI API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.sessions: Dict[str, ChatSession] = {}
        self.instruction_templates = self._load_instruction_templates()
    
    def _load_instruction_templates(self) -> Dict[str, str]:
        """Load berbagai template system instruction"""
        return {
            "general": """
                Anda adalah asisten AI yang membantu dalam berbagai topik.
                Jawab dengan informatif dan ramah.
                Gunakan bahasa Indonesia yang baik dan benar.
            """,
            
            "coding": """
                Anda adalah expert programmer yang membantu dengan:
                - Debug code
                - Optimasi kode
                - Code review
                - Arsitektur software
                Berikan penjelasan yang detail dan contoh yang praktis.
            """,
            
            "creative": """
                Anda adalah creative writer yang membantu dengan:
                - Penulisan kreatif
                - Brainstorming ide
                - Storytelling
                - Content creation
                Berikan respons yang imaginatif dan engaging.
            """,
            
            "business": """
                Anda adalah business consultant yang membantu dengan:
                - Strategi bisnis
                - Analisis pasar
                - Financial planning
                - Marketing strategy
                Berikan analisis yang mendalam dan actionable insights.
            """,
            
            "education": """
                Anda adalah tutor yang membantu dengan:
                - Penjelasan konsep
                - Pembelajaran step-by-step
                - Quiz dan evaluasi
                - Study guidance
                Jelaskan dengan sabar dan mudah dipahami.
            """
        }
    
    def get_or_create_session(self, user_id: str, instruction_type: str = "general") -> ChatSession:
        """
        Get existing session atau create new session
        
        Args:
            user_id: Telegram user ID
            instruction_type: Tipe instruction yang akan digunakan
            
        Returns:
            ChatSession object
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = ChatSession(
                user_id=user_id,
                history=[],
                instruction_type=instruction_type,
                created_at=self._get_current_time(),
                last_activity=self._get_current_time()
            )
        
        return self.sessions[user_id]
    
    def change_instruction_type(self, user_id: str, new_instruction_type: str) -> bool:
        """
        Ubah tipe instruction untuk user tertentu
        
        Args:
            user_id: Telegram user ID
            new_instruction_type: Tipe instruction baru
            
        Returns:
            True jika berhasil, False jika instruction type tidak ada
        """
        if new_instruction_type not in self.instruction_templates:
            return False
        
        session = self.get_or_create_session(user_id)
        session.instruction_type = new_instruction_type
        session.last_activity = self._get_current_time()
        
        return True
    
    def add_custom_instruction(self, name: str, instruction: str):
        """
        Tambah custom instruction template
        
        Args:
            name: Nama instruction template
            instruction: Isi instruction
        """
        self.instruction_templates[name] = instruction
    
    def send_message(self, user_id: str, message: str, instruction_type: Optional[str] = None) -> str:
        """
        Kirim message ke Gemini dan dapatkan response
        
        Args:
            user_id: Telegram user ID
            message: User message
            instruction_type: Override instruction type untuk message ini
            
        Returns:
            Response dari Gemini
        """
        session = self.get_or_create_session(user_id)
        
        # Override instruction type jika diberikan
        current_instruction_type = instruction_type or session.instruction_type
        
        # Ambil system instruction
        system_instruction = self.instruction_templates.get(
            current_instruction_type, 
            self.instruction_templates["general"]
        )
        
        try:
            # Buat chat dengan history dan system instruction
            chat = self.model.start_chat(
                history=session.history,
                system_instruction=system_instruction
            )
            
            # Kirim message
            response = chat.send_message(message)
            
            # Update history
            session.history.extend([
                {"role": "user", "parts": [message]},
                {"role": "model", "parts": [response.text]}
            ])
            
            session.last_activity = self._get_current_time()
            
            return response.text
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self, user_id: str):
        """Clear chat history untuk user tertentu"""
        if user_id in self.sessions:
            self.sessions[user_id].history = []
            self.sessions[user_id].last_activity = self._get_current_time()
    
    def get_available_instructions(self) -> List[str]:
        """Get list semua available instruction types"""
        return list(self.instruction_templates.keys())
    
    def get_session_info(self, user_id: str) -> Dict[str, Any]:
        """Get informasi session untuk user tertentu"""
        if user_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[user_id]
        return {
            "user_id": session.user_id,
            "instruction_type": session.instruction_type,
            "history_length": len(session.history),
            "created_at": session.created_at,
            "last_activity": session.last_activity
        }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Cleanup session yang sudah lama tidak aktif
        
        Args:
            max_age_hours: Maximum age dalam jam
        """
        # Implementation untuk cleanup berdasarkan timestamp
        # Bisa disesuaikan dengan kebutuhan
        pass
    
    def _get_current_time(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Contoh penggunaan dalam telegram bot
class TelegramBotExample:
    def __init__(self, gemini_api_key: str, telegram_token: str):
        self.chat_manager = GeminiChatManager(gemini_api_key)
        # Setup telegram bot disini
    
    def handle_message(self, user_id: str, message: str):
        """Handle incoming telegram message"""
        
        # Check jika message adalah command untuk ganti instruction
        if message.startswith('/mode'):
            parts = message.split()
            if len(parts) > 1:
                instruction_type = parts[1]
                if self.chat_manager.change_instruction_type(user_id, instruction_type):
                    return f"Mode berhasil diubah ke: {instruction_type}"
                else:
                    available = self.chat_manager.get_available_instructions()
                    return f"Mode tidak tersedia. Available: {', '.join(available)}"
        
        # Check command lainnya
        elif message == '/clear':
            self.chat_manager.clear_history(user_id)
            return "Chat history berhasil dihapus!"
        
        elif message == '/info':
            info = self.chat_manager.get_session_info(user_id)
            return f"Session info: {json.dumps(info, indent=2)}"
        
        elif message == '/modes':
            modes = self.chat_manager.get_available_instructions()
            return f"Available modes: {', '.join(modes)}"
        
        # Regular chat message
        else:
            return self.chat_manager.send_message(user_id, message)