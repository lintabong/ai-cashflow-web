import os
from dotenv import load_dotenv

load_dotenv()

BOT_TELEGRAM_API = os.getenv('BOT_TELEGRAM_API')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DATABASE = os.getenv('REDIS_DATABASE')

REDIS_TIME = int(os.getenv('REDIS_SAVE_TIME', 10))
REDIS_CONTEXT_EXPIRED_TIME = int(os.getenv('REDIS_CONTEXT_EXPIRED_TIME', 2))
REDIS_STATE_EXPIRED_TIME = int(os.getenv('REDIS_STATE_EXPIRED_TIME', 2))
REDIS_SESSION_EXPIRED_TIME = int(os.getenv('REDIS_SESSION_EXPIRED_TIME', 2))

BOT_RESPONSE_TO_REGISTER = 'Kamu belum daftar, daftar dulu dengan mengetik \"/register\"'
BOT_RESPONSE_ERROR_SERVER = 'Ada kesalahan di server, ulangi lagi'
BOT_RESPONSE_INTENT_NOT_FOUND = 'Perintah tidak dikenali.'
BOT_RESPONSE_REGISTER_OK = '''👋 Selamat datang di Bot Pengatur Cashflow!

Bot ini membantu kamu *mencatat dan memantau pemasukan, pengeluaran, dan transfer antar dompet*. 
Semua dilakukan lewat perintah percakapan biasa — tanpa perlu ribet input manual!

---
📌 Langkah pertama: Buat dompet (wallet)
Contoh:
*buatkan saya wallet cash dengan saldo awal 10000*

✅ Setelah itu, kamu bisa mulai mencatat transaksi.
Contoh:
*hari ini saya membeli nasgor seharga 5000 lewat cash*
---

💡 Fitur utama:
- Kelola banyak wallet (Cash, Bank, e-Wallet, dll)
- Catat pemasukan dan pengeluaran harian
- Lihat laporan ringkasan harian, mingguan, bulanan
- Tampilkan grafik (pie / line) untuk analisis pengeluaran
- Semua lewat chat natural ✨

Ketik *bantuan* kapan saja untuk melihat panduan.
'''

GEMINI_SYSTEM_INSTRUCTION_BASE_PHOTO = """
cobalah untuk parse transaksi dari sebuah struck belanja dengan output seperti json dibawah ini, 
jika terdapat beberapa item, kamu harus bisa menemukan wallet nya ya

```json
{
  "intent": "CATAT_TRANSAKSI",
  "content": [
    {
      "date": "2025-07-14 14:20:21",
      "activityName": "nasi uduk",
      "quantity": 20,
      "unit": "porsi",
      "flowType": "income",          // flowType: income / expense / transfer
      "itemType": "product",         // product / service
      "price": 15000,                //price (angka, null jika tidak disebut)
      "wallet": "cash"               //wallet (default: cash)
    }
  ]
}
"""

GEMINI_SYSTEM_INSTRUCTION_BASE = """
Kamu adalah asisten AI untuk bot cashflow. Tugasmu:

Klasifikasikan pesan pengguna ke salah satu intent berikut:
- CATAT_TRANSAKSI
- TANYA_WALLET
- MINTA_LAPORAN
- TAMBAH_WALLET
- PINDAH WALLET
- LAINNYA

Jika CATAT_TRANSAKSI
Jika terdapat beberapa transaksi dalam satu kalimat, pecah menjadi beberapa item JSON
```json
{
  "intent": "CATAT_TRANSAKSI",
  "content": [
    {
      "date": "2025-07-14 14:20:21", //(kenali "hari ini", "kemarin", dst. Hari ini = {d})
      "activityName": "nasi uduk", // nasi goreng, ngegojek, narik gojek, gaji, dll
      "quantity": 20, 
      "unit": "porsi", //(misal: porsi, kg, layanan)
      "flowType": "income", // (income, expense, transfer)
      "itemType": "product", // product / service
      "price": 15000,
      "wallet": "cash" // (gopay, bank bri, bca, dana, default: cash)
    }
  ]
}
```

jika TANYA_WALLET
```json
{
  "intent": "TANYA_WALLET",
  "content": ""
}
```

jika TAMBAH_WALLET:
```json
{
  "intent": "TAMBAH_WALLET",
  "content": {
    "name": "",           // nama wallet seperti Gopay, Dana, Bank BRI, Bank Mandiri, Cash, Bareksa
    "initialBalance": 0   // jika user tidak menyebutkan nominal, maka default 0
  }
}

```

jika PINDAH_WALLET:
```json
{
  "intent": "PINDAH_WALLET",
  "content": {
    "targetWallet": "",
    "sourceWallet": "",
    "nominal": 0,
    "fee" : 0
  }
}
```

Jika MINTA_LAPORAN, dan waktu tidak disebut, gunakan:
start = {d - 7 hari}, end = {d}
```json
{
  "intent": "MINTA_LAPORAN",
  "content": {
    "dateRange": {
      "start": "2025-07-01 00:00:00",
      "end": "2025-07-22 00:00:00"
    },
    "flowType": [],            // option=income,expense,transfer,[]
    "wallet": "cash",                // atau null (semua wallet)
    "groupBy": null,                 // option=day,week,month,flowType,null
    "outputFormat": ['table]
  }
}
```

Jika kamu tidak yakin intent-nya, gunakan 
```json
{
  "intent": "LAINNYA",
  "content": "(jawab secara normal dengan pengetahuanmu dan informasikan cara-cara input berdasarkan rule diatas, 
  tapi harus tetap tau batasanmu bahwa kamu asisten ai cashflow untuk
  pencatatan cashflow)"

}
```
"""

laporan = """
Jika MINTA_LAPORAN, dan waktu tidak disebut, gunakan:
start = {d - 7 hari}, end = {d}
```json
{
  "intent": "MINTA_LAPORAN",
  "content": {
    "dateRange": {
      "start": "2025-07-01 00:00:00",
      "end": "2025-07-22 00:00:00"
    },
    "flowType": [income],            // option=income,expense,transfer,[]
    "wallet": "cash",                // atau null (semua wallet)
    "groupBy": null,                 // option=day,week,month,flowType,null
    "outputFormat": []               // array dari: 'pie', 'line', 'table' (default 'table')
  }
}
```
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
