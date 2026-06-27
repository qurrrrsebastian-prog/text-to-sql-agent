"""Text-to-SQL Agent — Groq (Llama 3.3 70B) | v2.0 production upgrade.

Emerald Query theme, tabbed layout (Query · Schema · History). v2.0 adds SQLite
metadata persistence (query history, schema cache, audit log), a schema browser,
re-runnable query history, SQL injection / read-only guarding, result pagination,
execution-time metrics and CSV export. Lazy Groq client keeps the UI usable
without an API key.

Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import os
import sqlite3
import sys
import time

import pandas as pd
import streamlit as st

import database as db
from security import is_safe_sql, sanitize_input
from ui_components import render_footer, render_header, render_status_badge

st.set_page_config(page_title="Text-to-SQL Agent", layout="wide", page_icon="🗣️")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "rkari_sales.db")
PAGE_SIZE = 50

db.init_db()


# --------------------------------------------------------------------------- #
# Setup / helpers
# --------------------------------------------------------------------------- #
@st.cache_resource
def ensure_target_db() -> bool:
    """Create the demo database and cache its schema once."""
    if not os.path.exists(DB_PATH):
        os.system(f'"{sys.executable}" data/setup_db.py')
    db.refresh_schema_cache(DB_PATH)
    return True


ensure_target_db()


@st.cache_resource(show_spinner=False)
def get_llm():
    """Return a cached Groq chat model, or None if no API key."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", api_key=key, temperature=0.1)
    except Exception:  # noqa: BLE001
        return None


def get_full_schema() -> str:
    """Return all CREATE TABLE statements from the target DB."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'").fetchall()
        conn.close()
        return "\n\n".join(r[0] for r in rows if r[0])
    except Exception as exc:  # noqa: BLE001
        return f"-- schema error: {exc}"


def generate_sql(question: str, schema: str, llm) -> str:
    """Generate SQL from natural language using Groq."""
    prompt = (f"You are a SQL expert. Given this schema:\n{schema}\n\n"
              "Convert this question to a valid SQLite SQL query. Return ONLY the "
              f"SQL, no explanation.\nQuestion: {question}")
    sql = llm.invoke(prompt).content.strip()
    if sql.startswith("```"):
        sql = sql.split("```")[1].replace("sql", "", 1).strip()
    return sql


def run_sql(query: str):
    """Execute a read-only SQL query. Returns (df, elapsed_ms, success, error)."""
    safe, reason = is_safe_sql(query)
    if not safe:
        return pd.DataFrame(), 0.0, False, reason
    start = time.perf_counter()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        elapsed = (time.perf_counter() - start) * 1000
        return df, elapsed, True, ""
    except Exception as exc:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return pd.DataFrame(), elapsed, False, str(exc)


def show_result(df: pd.DataFrame) -> None:
    """Display a result DataFrame with pagination for large results."""
    if df.empty:
        st.info("Query returned no rows.")
        return
    if len(df) > PAGE_SIZE:
        pages = (len(df) - 1) // PAGE_SIZE + 1
        page = st.number_input(f"Page (1–{pages}, {len(df)} rows)", 1, pages, 1)
        lo = (page - 1) * PAGE_SIZE
        st.dataframe(df.iloc[lo:lo + PAGE_SIZE], use_container_width=True,
                     hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="query_result.csv", mime="text/csv")


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
llm = get_llm()
render_header("🗣️ Text-to-SQL Agent",
              "Ask in natural language → AI generates SQL → results · v2.0 Emerald Query")
if llm is None:
    st.info("ℹ️ GROQ_API_KEY not set — SQL generation is disabled. You can still "
            "browse the schema, run history, and execute SQL manually below.")

if "pending_sql" not in st.session_state:
    st.session_state.pending_sql = ""

tab_query, tab_schema, tab_history = st.tabs(["🔍 Query", "🗂️ Schema", "🕑 History"])

# --------------------------------------------------------------------------- #
# TAB — Query
# --------------------------------------------------------------------------- #
with tab_query:
    schema = get_full_schema()
    question = st.text_input("❓ Pertanyaan:",
                             "Berapa total contract value klien aktif?")
    gen = st.button("🤖 Generate SQL", type="primary", disabled=llm is None)
    if gen and question:
        with st.spinner("Generating SQL..."):
            try:
                st.session_state.pending_sql = generate_sql(
                    sanitize_input(question, 500), schema, llm)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Generation error: {exc}")

    sql_text = st.text_area("📝 SQL (editable)", st.session_state.pending_sql,
                            height=120)
    safe, reason = is_safe_sql(sql_text) if sql_text.strip() else (False, "")
    if sql_text.strip():
        if safe:
            render_status_badge("✓ read-only query", "#059669")
        else:
            render_status_badge(f"⚠ {reason}", "#DC2626")
    st.code(sql_text or "-- generated SQL appears here", language="sql")

    if st.button("▶️ Run SQL") and sql_text.strip():
        result, ms, ok, err = run_sql(sql_text)
        db.add_query(question, sql_text, ms, len(result), ok)
        db.add_log("run_sql", f"ok={ok}, rows={len(result)}")
        if ok:
            mc1, mc2 = st.columns(2)
            mc1.metric("Rows", len(result))
            mc2.metric("Execution time", f"{ms:.1f} ms")
            st.subheader("📊 Result")
            show_result(result)
        else:
            st.error(f"Query failed: {err}")

# --------------------------------------------------------------------------- #
# TAB — Schema browser
# --------------------------------------------------------------------------- #
with tab_schema:
    st.subheader("🗂️ Database Schema")
    if st.button("🔄 Refresh schema cache"):
        n = db.refresh_schema_cache(DB_PATH)
        st.success(f"Cached {n} columns.")
        st.rerun()
    cache = db.get_schema_cache()
    if cache.empty:
        db.refresh_schema_cache(DB_PATH)
        cache = db.get_schema_cache()
    for table in cache["table_name"].unique():
        st.markdown(f"#### 📋 `{table}`")
        st.dataframe(cache[cache["table_name"] == table]
                     [["column_name", "data_type", "sample_values"]],
                     use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("##### Raw DDL")
    st.code(get_full_schema(), language="sql")

# --------------------------------------------------------------------------- #
# TAB — History
# --------------------------------------------------------------------------- #
with tab_history:
    st.subheader("🕑 Query History")
    hist = db.get_query_history()
    if hist.empty:
        st.caption("No queries run yet.")
    else:
        hc1, hc2 = st.columns([3, 1])
        hc1.metric("Total queries", len(hist))
        if hc2.button("🗑️ Clear history"):
            db.clear_query_history()
            st.rerun()
        for _, h in hist.head(50).iterrows():
            ok = "✅" if h["success"] else "❌"
            with st.expander(f"{ok} {h['natural_language'][:60]} · "
                             f"{h['execution_time_ms']:.0f} ms · {h['row_count']} rows"):
                st.code(h["generated_sql"], language="sql")
                if st.button("↻ Re-run this query", key=f"rerun_{h['id']}"):
                    st.session_state.pending_sql = h["generated_sql"]
                    st.toast("Loaded into the Query tab editor.", icon="↻")
        st.divider()
        st.download_button("⬇️ Export history CSV",
                           hist.to_csv(index=False).encode("utf-8"),
                           file_name="query_history.csv", mime="text/csv")

render_footer()
