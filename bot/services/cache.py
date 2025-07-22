import redis
import json
import time
from bot.constants import (
    REDIS_HOST, 
    REDIS_PORT, 
    REDIS_PASSWORD, 
    REDIS_TIME, 
    REDIS_DATABASE
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CacheMessage:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            password=REDIS_PASSWORD,
            db=REDIS_DATABASE,
            decode_responses=True
        )

    def save_message(self, user_id, text, role):
        message_data = {
            'id': int(time.time()),
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'role': role
        }

        logger.info(f'Saving {user_id}')
        self.save_context(user_id, message_data)
        
    def save_context(self, user_id, message_data):
        """Simpan konteks percakapan"""
        key = f"user:context:{user_id}"
        
        # Ambil konteks yang ada
        existing_context = self.get_context(user_id)
        
        if existing_context:
            existing_context['messages'].append(message_data)
            existing_context['updated_at'] = datetime.now().isoformat()
        else:
            existing_context = {
                'messages': [message_data],
                'topic': 'general',
                'intent': None,
                'entities': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        # Batasi jumlah pesan (maksimal 20)
        if len(existing_context['messages']) > 20:
            existing_context['messages'] = existing_context['messages'][-20:]
        
        # Simpan dengan TTL 
        self.redis_client.setex(
            key, 
            REDIS_TIME*60, 
            json.dumps(existing_context)
        )
        
        # Update last activity
        self.update_last_activity(user_id)
    
    def get_context(self, user_id):
        """Ambil konteks percakapan"""
        key = f"user:context:{user_id}"
        context_data = self.redis_client.get(key)
        
        if context_data:
            return json.loads(context_data)
        return None
    
    def save_session(self, user_id, session_data):
        """Simpan session user"""
        key = f"user:session:{user_id}"
        self.redis_client.setex(
            key, 
            REDIS_TIME*60*10,  # 1 jam
            json.dumps(session_data)
        )
    
    def get_session(self, user_id):
        """Ambil session user"""
        key = f"user:session:{user_id}"
        session_data = self.redis_client.get(key)
        
        if session_data:
            return json.loads(session_data)
        return None
    
    def save_state(self, user_id, state_data):
        """Simpan state conversation"""
        key = f"user:state:{user_id}"
        self.redis_client.setex(
            key, 
            REDIS_TIME*60*10,  # 30 menit
            json.dumps(state_data)
        )
    
    def get_state(self, user_id):
        """Ambil state conversation"""
        key = f"user:state:{user_id}"
        state_data = self.redis_client.get(key)
        
        if state_data:
            return json.loads(state_data)
        return None
    
    def update_last_activity(self, user_id):
        """Update timestamp aktivitas terakhir"""
        key = f"user:last_activity:{user_id}"
        self.redis_client.setex(
            key, 
            REDIS_TIME*60,
            str(int(time.time()))
        )
    
    def is_context_expired(self, user_id):
        """Cek apakah konteks sudah expired"""
        key = f"user:context:{user_id}"
        return not self.redis_client.exists(key)
    
    def clear_user_data(self, user_id):
        """Hapus semua data user"""
        keys_to_delete = [
            f"user:context:{user_id}",
            f"user:session:{user_id}",
            f"user:state:{user_id}",
            f"user:last_activity:{user_id}",
            f"user:message_count:{user_id}"
        ]
        
        for key in keys_to_delete:
            self.redis_client.delete(key)
    
    def extend_context_ttl(self, user_id):
        """Perpanjang TTL konteks (jika masih dalam sesi aktif)"""
        key = f"user:context:{user_id}"
        if self.redis_client.exists(key):
            self.redis_client.expire(key, REDIS_TIME*60)  # Reset ke 10 menit
