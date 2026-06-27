# Project #12 — Text-to-SQL Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
</p>

> Konversi natural language ke query SQL otomatis. Untuk non-technical users yang butuh data dari database tanpa nulis SQL.

---

## Demo Langsung

[![Deploy to Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/deploy?repository=qurrrrsebastian-prog/text-to-sql-agent)

**Tech Stack:** `LangChain` · `SQLite` · `Google Gemini API` · `Streamlit`

---

## Fitur

| Fitur | Status |
|-------|--------|
| NL to SQL query generation | ✅ |
| Eksekusi query otomatis | ✅ |
| Hasil dalam tabel interaktif | ✅ |
| Validasi query safety | ✅ |
| Database contoh built-in | ✅ |
| Tema gelap AVA purple | ✅ |

---

## Cara Menjalankan

```bash
git clone https://github.com/qurrrrsebastian-prog/text-to-sql-agent.git
cd text-to-sql-agent
pip install -r requirements.txt
$env:GEMINI_API_KEY="your_api_key_here"
streamlit run app.py
```

## Deploy ke Streamlit Cloud (GRATIS)

1. [share.streamlit.io](https://share.streamlit.io) → Login GitHub
2. **New app** → Pilih repo ini
3. Tambahkan secret: `GEMINI_API_KEY`
4. **Deploy**

---

## Struktur Project

```
text-to-sql-agent/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── data/               # Sample database
├── .streamlit/
│   └── config.toml    # AVA purple branding
├── .gitignore
└── LICENSE            # MIT License
```

---

**Dibuat oleh:** [Avatar Putra Sigit](https://github.com/qurrrrsebastian-prog) · Founder @AVA.Group
