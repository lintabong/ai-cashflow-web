import requests
import os
import tempfile
import hashlib
import hmac
import base64
from datetime import datetime
from urllib.parse import quote
from telegram import File
from bot.constants import (
    S3_ACCESS_KEY,
    S3_BUCKET,
    S3_ENDPOINT,
    S3_SECRET_KEY
)

class ImageManager:
    def __init__(self):
        self.endpoint_url = S3_ENDPOINT.rstrip("/")
        self.access_key = S3_ACCESS_KEY
        self.secret_key = S3_SECRET_KEY
        self.bucket_name = S3_BUCKET

    def _create_signature(self, string_to_sign):
        return base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'), 
                string_to_sign.encode('utf-8'), 
                hashlib.sha1
            ).digest()
        ).decode('utf-8')

    def _get_auth_headers(self, method, object_name, content_type="image/jpeg"):
        timestamp = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        string_to_sign = f"{method}\n\n{content_type}\n{timestamp}\n/{self.bucket_name}/{object_name}"
        signature = self._create_signature(string_to_sign)
        
        return {
            'Date': timestamp,
            'Content-Type': content_type,
            'Authorization': f'AWS {self.access_key}:{signature}'
        }

    async def upload_image(self, telegram_file: File, user_id: int) -> str:
        file_path = None
        try:
            # Buat temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
                file_path = tf.name
            
            # Download file dari Telegram
            await telegram_file.download_to_drive(file_path)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{os.path.basename(file_path)}"
            object_name = f"uploads/{user_id}/{filename}"
            
            # URL untuk S3
            url = f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
            
            # Baca file content
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Generate headers dengan proper AWS signature
            headers = self._get_auth_headers("PUT", object_name, "image/jpeg")
            
            # Upload ke S3
            response = requests.put(
                url,
                data=file_content,
                headers=headers,
                timeout=30  # Add timeout
            )
            
            if response.status_code in [200, 201]:
                # Return URL akses file
                file_url = f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
                return f"✅ Foto berhasil di-upload!\n🔗 URL: {file_url}\n📁 Path: `{object_name}`"
            else:
                print(f"Response text: {response.text}")
                return f"❌ Upload gagal, status {response.status_code}: {response.text}"

        except Exception as e:
            print(f"Upload error: {str(e)}")
            return f"❌ Gagal upload: {str(e)}"
        
        finally:
            # Cleanup temporary file
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Temp file removed: {file_path}")
                except Exception as e:
                    print(f"Failed to remove temp file: {e}")

    async def upload_image_multipart(self, telegram_file: File, user_id: int) -> str:
        """
        Alternative: Upload menggunakan multipart form (untuk beberapa S3 compatible services)
        """
        file_path = None
        try:
            # Buat temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
                file_path = tf.name
            
            # Download file dari Telegram
            await telegram_file.download_to_drive(file_path)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{user_id}.jpg"
            object_name = f"uploads/{user_id}/{filename}"
            
            # URL untuk upload
            url = f"{self.endpoint_url}/{self.bucket_name}"
            
            # Prepare multipart data
            with open(file_path, "rb") as f:
                files = {
                    'file': (filename, f, 'image/jpeg')
                }
                data = {
                    'key': object_name,
                    'AWSAccessKeyId': self.access_key,
                    'acl': 'public-read'  # Adjust based on your needs
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code in [200, 201, 204]:
                file_url = f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
                return f"✅ Foto berhasil di-upload!\n🔗 URL: {file_url}"
            else:
                return f"❌ Upload gagal, status {response.status_code}: {response.text}"

        except Exception as e:
            return f"❌ Gagal upload: {str(e)}"
        
        finally:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to remove temp file: {e}")

    def test_connection(self) -> bool:
        """
        Test koneksi ke S3 endpoint
        """
        try:
            # Test dengan HEAD request ke bucket
            url = f"{self.endpoint_url}/{self.bucket_name}"
            headers = self._get_auth_headers("HEAD", "", "")
            
            response = requests.head(url, headers=headers, timeout=10)
            return response.status_code in [200, 403]  # 403 might mean bucket exists but no list permission
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
