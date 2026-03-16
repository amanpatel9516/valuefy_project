"""
Initialize the SQLite database with schema and seed data.
Run this once: python init_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_portfolio.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── Tables ──────────────────────────────────────────────
    c.executescript("""
    DROP TABLE IF EXISTS rebalance_items;
    DROP TABLE IF EXISTS rebalance_sessions;
    DROP TABLE IF EXISTS client_holdings;
    DROP TABLE IF EXISTS model_funds;
    DROP TABLE IF EXISTS clients;

    CREATE TABLE clients (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL
    );

    CREATE TABLE model_funds (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        fund_name   TEXT NOT NULL,
        target_pct  REAL NOT NULL
    );

    CREATE TABLE client_holdings (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id   INTEGER NOT NULL,
        fund_name   TEXT NOT NULL,
        current_value REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    );

    CREATE TABLE rebalance_sessions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id       INTEGER NOT NULL,
        date            TEXT NOT NULL,
        portfolio_value REAL NOT NULL,
        total_buy       REAL NOT NULL,
        total_sell      REAL NOT NULL,
        net_cash_needed REAL NOT NULL,
        status          TEXT NOT NULL DEFAULT 'Recommended',
        FOREIGN KEY (client_id) REFERENCES clients(id)
    );

    CREATE TABLE rebalance_items (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id      INTEGER NOT NULL,
        fund_name       TEXT NOT NULL,
        target_pct      REAL,
        current_pct     REAL NOT NULL,
        drift           REAL,
        action          TEXT NOT NULL,
        amount          REAL NOT NULL,
        FOREIGN KEY (session_id) REFERENCES rebalance_sessions(id)
    );
    """)

    # ── Seed Data ───────────────────────────────────────────

    # Client
    c.execute("INSERT INTO clients (name) VALUES (?)", ("Amit Sharma",))
    client_id = c.lastrowid

    # Model Portfolio (recommended plan)
    model_funds = [
        ("Mirae Asset Large Cap Fund",      30.0),
        ("Parag Parikh Flexi Cap Fund",     25.0),
        ("HDFC Mid Cap Opportunities Fund", 20.0),
        ("ICICI Prudential Bond Fund",      15.0),
        ("Nippon India Gold ETF",           10.0),
    ]
    c.executemany("INSERT INTO model_funds (fund_name, target_pct) VALUES (?, ?)", model_funds)

    # Current Holdings
    holdings = [
        (client_id, "Mirae Asset Large Cap Fund",       90000),
        (client_id, "Parag Parikh Flexi Cap Fund",      155000),
        (client_id, "HDFC Mid Cap Opportunities Fund",  0),
        (client_id, "ICICI Prudential Bond Fund",       110000),
        (client_id, "Nippon India Gold ETF",            145000),
        (client_id, "Axis Bluechip Fund",               80000),
    ]
    c.executemany("INSERT INTO client_holdings (client_id, fund_name, current_value) VALUES (?, ?, ?)", holdings)

    conn.commit()
    conn.close()
    print(f"✅ Database created and seeded at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
