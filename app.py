"""Text-to-SQL Agent with Gemini. Author: Avatar Putra Sigit"""
import os
import sys
import sqlite3
import pandas as pd
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "rkari_sales.db")

def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize Gemini."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        st.error("GEMINI_API_KEY not found.")
        sys.exit(1)
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=key, temperature=0.1)

def get_schema() -> str:
    """Get SQLite schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='clients'")
    schema = c.fetchone()[0]
    conn.close()
    return schema

def run_sql(query: str) -> pd.DataFrame:
    """Execute SQL safely."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def generate_sql(question: str, schema: str, llm: ChatGoogleGenerativeAI) -> str:
    """Generate SQL from natural language using Gemini."""
    prompt = f"""You are a SQL expert. Given this schema:
{schema}

Convert this question to a valid SQLite SQL query. Return ONLY the SQL, no explanation.
Question: {question}"""
    response = llm.invoke(prompt)
    sql = response.content.strip()
    if sql.startswith("```"):
        sql = sql.split("```")[1].replace("sql", "").strip()
    return sql

def main() -> None:
    st.set_page_config(page_title="Text-to-SQL Agent", layout="wide")
    st.title("🗣️ Text-to-SQL Agent — Gemini Powered")
    st.markdown("Tanya data RKARI dalam bahasa Indonesia → AI generate SQL → tampilkan hasil")

    if not os.path.exists(DB_PATH):
        os.system(f"{sys.executable} data/setup_db.py")

    schema = get_schema()
    llm = get_llm()

    st.subheader("📋 Database Schema")
    st.code(schema, language="sql")

    question = st.text_input("❓ Pertanyaan:", "Berapa total contract value klien aktif?")
    if st.button("🔍 Generate & Run SQL", type="primary") and question:
        with st.spinner("Generating SQL..."):
            sql = generate_sql(question, schema, llm)
            st.subheader("📝 Generated SQL")
            st.code(sql, language="sql")

            result = run_sql(sql)
            st.subheader("📊 Hasil")
            st.dataframe(result, use_container_width=True)

if __name__ == "__main__":
    main()
