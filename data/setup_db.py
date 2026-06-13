"""Setup SQLite database for Text-to-SQL demo. Author: Avatar Putra Sigit"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rkari_sales.db")

def init_db() -> None:
    """Create sample RKARI sales database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, company_name TEXT, industry TEXT, contract_value REAL, service_type TEXT, last_order_date TEXT, status TEXT)")

    sample = [
        (1, "PT Mega Tower", "Property", 45000000, "rope_access", "2024-05-15", "active"),
        (2, "Hotel Grand Indonesia", "Hotel", 28000000, "glass_cleaning", "2024-06-01", "active"),
        (3, "RS Siloam", "Hospital", 15000000, "maintenance", "2024-04-20", "inactive"),
        (4, "Mall Taman Anggrek", "Retail", 35000000, "rope_access", "2024-05-28", "active"),
        (5, "Kantor Kemenkeu", "Office", 22000000, "glass_cleaning", "2024-06-10", "active")
    ]
    c.executemany("INSERT OR IGNORE INTO clients VALUES (?,?,?,?,?,?,?)", sample)
    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")

if __name__ == "__main__":
    init_db()
