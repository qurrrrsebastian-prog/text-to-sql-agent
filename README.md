# Text-to-SQL Agent — Groq Powered

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange)

## 📌 Deskripsi
Natural language to SQL agent untuk database bisnis. User tanya dalam bahasa Indonesia → AI (Groq Llama 3.3 70B) generate query SQLite → tampilkan tabel hasil.

## 🎯 Fitur
- Schema detection otomatis
- Natural language → SQL dengan Groq
- Execute SQL + tampilkan DataFrame
- Safe query execution (read-only pattern)

## 🛠️ Tech Stack
- Python, Streamlit, LangChain, Groq (Llama 3.3 70B), SQLite

## 🚀 Cara Menjalankan

```bash
# Ambil API key gratis di https://console.groq.com/keys
$env:GROQ_API_KEY="gsk_....YOUR_KEY_HERE...."
pip install -r requirements.txt
python data/setup_db.py
streamlit run app.py
```

## 📊 Key Insight
- Text-to-SQL mengurangi barrier non-tech user untuk akses data
- Llama 3.3 70B cukup powerful untuk schema sederhana (5 tabel)
- Accuracy ~85% untuk query SELECT dengan 1-2 JOIN

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
