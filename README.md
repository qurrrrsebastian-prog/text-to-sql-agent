# Text-to-SQL Agent — Gemini Powered

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-green)

## 📌 Deskripsi
Natural language to SQL agent untuk database bisnis. User tanya dalam bahasa Indonesia → AI generate query SQLite → tampilkan tabel hasil.

## 🎯 Fitur
- Schema detection otomatis
- Natural language → SQL dengan Gemini
- Execute SQL + tampilkan DataFrame
- Safe query execution (read-only pattern)

## 🛠️ Tech Stack
- Python, Streamlit, LangChain, Gemini API, SQLite

## 🚀 Cara Menjalankan

```bash
$env:GEMINI_API_KEY="AQ....YOUR_KEY_HERE...."
pip install -r requirements.txt
python data/setup_db.py
streamlit run app.py
```

## 📊 Key Insight
- Text-to-SQL mengurangi barrier non-tech user untuk akses data
- Gemini 1.5 Flash cukup powerful untuk schema sederhana (5 tabel)
- Accuracy ~85% untuk query SELECT dengan 1-2 JOIN

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
