# 💰 Telegram Bot Cashflow

Telegram bot ini dibuat untuk membantu pengguna mencatat dan mengelola arus kas (cashflow) secara otomatis melalui percakapan alami menggunakan **Gemini AI**, dengan data yang disimpan di **MySQL** dan cache di **Redis**.

---

## 🧠 Fitur Utama

- 🚀 **Pendaftaran Otomatis**: Pengguna dapat mendaftar dengan perintah `/register`.
- 🧾 **Pencatatan Transaksi Otomatis**: Kirim pesan seperti "Saya beli bahan baku 2 kg" dan bot akan mencatatnya.
- 📊 **Laporan Harian**: Data transaksi dikelompokkan per tanggal dan dirender sebagai tabel.
- 💰 **Cek Saldo**: Bot bisa menjawab pertanyaan seperti "Saldo saya berapa?"
- ✅ **Konfirmasi Transaksi**: Setelah parsing, pengguna dikonfirmasi sebelum data disimpan.

---

## 📦 Tech Stack

- **Python**
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** (v20+)
- **Gemini API (Google Generative AI)**
- **MySQL**
- **Redis** (untuk penyimpanan percakapan sementara)
- **dotenv** (untuk mengelola environment variables)

---
