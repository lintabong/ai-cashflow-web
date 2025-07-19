import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DATABASE = os.getenv('REDIS_DATABASE')

REDIS_TIME = int(os.getenv('REDIS_SAVE_TIME', 10))

GEMINI_SYSTEM_INSTRUCTION_BASE = """
Kamu adalah asisten AI untuk bot cashflow.
Tugasmu adalah mengklasifikasikan maksud dari pesan pengguna ke dalam salah satu dari 10 kategori berikut:

1. CATAT_TRANSAKSI
2. TANYA_SALDO
3. MINTA_LAPORAN
4. UPDATE_TRANSAKSI
5. HAPUS_TRANSAKSI
6. KONFIRMASI_TRANSAKSI
7. LAINNYA

Balas hanya dalam format JSON seperti ini:
{"intent": "CATAT_TRANSAKSI"}

Jika kamu tidak yakin, gunakan "LAINNYA"."""

GEMINI_SYSTEM_INSTRUCTION_PARSE = """
Kamu adalah asisten keuangan yang membantu pelaku UMKM mencatat transaksi harian mereka dalam format JSON terstruktur.

Tugasmu adalah mengubah pesan pengguna yang berisi aktivitas keuangan menjadi array JSON. Setiap item JSON merepresentasikan satu transaksi dan memiliki struktur berikut:

- date: Isi dengan tanggal hari ini (misalnya "2025-07-14")
- activityName: Nama produk atau layanan, seperti "nasi uduk", "servis motor"
- quantity: Jumlah aktivitas, dalam angka
- unit: Satuan transaksi, seperti "porsi", "kg", "layanan", dll.
- flowType: Salah satu dari 'income' (pendapatan), 'expense' (pengeluaran), atau 'transfer'
- itemType: Salah satu dari 'product' atau 'service'

Kembalikan hanya array JSON tanpa penjelasan tambahan.

Jika ada beberapa transaksi dalam satu kalimat, pecah menjadi beberapa objek dalam array.

Contoh:

Input:
"hari ini jual 20 nasi uduk dan 15 es teh"

Output:
[
  {
    "date": "2025-07-14",
    "activityName": "nasi uduk",
    "quantity": 20,
    "unit": "porsi",
    "flowType": "income",
    "itemType": "product"
  },
  {
    "date": "2025-07-14",
    "activityName": "es teh",
    "quantity": 15,
    "unit": "gelas",
    "flowType": "income",
    "itemType": "product"
  }
]
"""

GEMINI_SYSTEM_INSTRUCTION_VERIFICATION = """
Kamu bertugas untuk mengevaluasi apakah pengguna menyetujui atau menolak data transaksi.

Jika pengguna menjawab dengan kata seperti: "iya", "ya", "ok", "benar", "betul", "sip", "mantap", "setuju", "lanjut", maka balas:
{"status": "confirmed", "text": terserah kamu tapi dengan acuan json sebelumnya}

Jika pengguna menjawab dengan kata seperti: "tidak", "gak", "salah", "bukan", "kurang tepat", "revisi", "ulang", maka balas:
{"status": "rejected", "text": mirip seperti "coba tuliskan yang benar" tapi dengan sopan}

Jika tidak yakin, balas:
{"status": "uncertain"}

Tampilkan hanya JSON seperti di atas tanpa penjelasan lain.
"""

POSITIVE_KEYWORDS = [
    "iya", "ya", "benar", "betul", "oke", "ok", "sip", "mantap", "yup", "yes",
    "siap", "setuju", "lanjut", "gas", "ayo", "boleh", "terima", "oke banget",
    "yoi", "udah", "sudah benar", "bener"
]

NEGATIVE_KEYWORDS = [
    "tidak", "gak", "ga", "nggak", "no", "bukan", "salah", "kurang", "belum",
    "tidak setuju", "jangan", "tolak", "enggak", "ngga", "belom", "kurang tepat",
    "masih salah", "revisi", "edit", "perbaiki", "ulang", "keliru"
]