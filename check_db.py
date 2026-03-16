"""Quick script to show all tables and data in the database."""
import sqlite3, os

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_portfolio.db')
conn = sqlite3.connect(db)
c = conn.cursor()

print("=" * 50)
print("DATABASE TABLES")
print("=" * 50)
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    count = c.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"  📋 {t[0]} ({count} rows)")

print("\n" + "=" * 50)
print("CLIENT")
print("=" * 50)
for r in c.execute("SELECT * FROM clients").fetchall():
    print(f"  👤 ID={r[0]}, Name={r[1]}")

print("\n" + "=" * 50)
print("MODEL FUNDS (Target Plan)")
print("=" * 50)
for r in c.execute("SELECT * FROM model_funds").fetchall():
    print(f"  🎯 {r[1]}: {r[2]}%")

print("\n" + "=" * 50)
print("CLIENT HOLDINGS")
print("=" * 50)
total = 0
for r in c.execute("SELECT * FROM client_holdings").fetchall():
    print(f"  💰 {r[2]}: ₹{r[3]:,.0f}")
    total += r[3]
print(f"  ─────────────────────────────")
print(f"  TOTAL: ₹{total:,.0f}")

print("\n" + "=" * 50)
print("REBALANCE SESSIONS (Saved History)")
print("=" * 50)
sessions = c.execute("SELECT * FROM rebalance_sessions").fetchall()
if sessions:
    for r in sessions:
        print(f"  📅 {r[2]} | Portfolio: ₹{r[3]:,.0f} | Buy: ₹{r[4]:,.0f} | Sell: ₹{r[5]:,.0f} | Status: {r[7]}")
else:
    print("  (No sessions saved yet - click Save Recommendation in the app)")

conn.close()
