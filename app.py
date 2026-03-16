"""
Portfolio Rebalancing Web App — Flask Backend
"""
import sqlite3
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_portfolio.db')


# ── Helpers ─────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_client_id():
    """Return the first client id (Amit Sharma)."""
    conn = get_db()
    row = conn.execute("SELECT id FROM clients LIMIT 1").fetchone()
    conn.close()
    return row["id"] if row else None


# ── Core Calculation ────────────────────────────────────────

def calculate_rebalance(client_id, conn=None):
    close_conn = False
    if conn is None:
        conn = get_db()
        close_conn = True

    # Get current holdings
    holdings = conn.execute(
        "SELECT fund_name, current_value FROM client_holdings WHERE client_id = ?",
        (client_id,)
    ).fetchall()

    # Get model funds (target plan)
    model_funds = conn.execute("SELECT fund_name, target_pct FROM model_funds").fetchall()

    if close_conn:
        conn.close()

    # Build lookup maps
    holdings_map = {h["fund_name"]: h["current_value"] for h in holdings}
    model_map = {m["fund_name"]: m["target_pct"] for m in model_funds}

    # Total portfolio value
    total_value = sum(holdings_map.values())
    if total_value == 0:
        return [], 0, 0, 0, 0

    # Collect all unique fund names
    all_funds = set(holdings_map.keys()) | set(model_map.keys())

    results = []
    total_buy = 0
    total_sell = 0

    for fund in sorted(all_funds):
        current_value = holdings_map.get(fund, 0)
        target_pct = model_map.get(fund, None)

        current_pct = round((current_value / total_value) * 100, 2) if total_value else 0

        if target_pct is None:
            # Fund is NOT in the recommended plan → REVIEW
            drift = None
            action = "REVIEW"
            amount = current_value
        else:
            drift = round(target_pct - current_pct, 2)
            amount = round(abs(drift / 100 * total_value), 2)
            if drift > 0:
                action = "BUY"
                total_buy += amount
            elif drift < 0:
                action = "SELL"
                total_sell += amount
            else:
                action = "HOLD"

        results.append({
            "fund_name": fund,
            "target_pct": target_pct,
            "current_pct": current_pct,
            "drift": drift,
            "action": action,
            "amount": round(amount, 2),
        })

    net_cash = round(total_buy - total_sell, 2)

    return results, total_value, round(total_buy, 2), round(total_sell, 2), net_cash


# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# Screen 1: Portfolio Comparison
@app.route("/api/portfolio")
def api_portfolio():
    client_id = get_client_id()
    items, total_value, total_buy, total_sell, net_cash = calculate_rebalance(client_id)
    return jsonify({
        "client_id": client_id,
        "portfolio_value": total_value,
        "total_buy": total_buy,
        "total_sell": total_sell,
        "net_cash_needed": net_cash,
        "items": items,
    })


# Screen 2: Current Investments
@app.route("/api/holdings")
def api_holdings():
    client_id = get_client_id()
    conn = get_db()
    rows = conn.execute(
        "SELECT fund_name, current_value FROM client_holdings WHERE client_id = ?",
        (client_id,)
    ).fetchall()
    client = conn.execute("SELECT name FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    holdings = [{"fund_name": r["fund_name"], "current_value": r["current_value"]} for r in rows]
    total = sum(h["current_value"] for h in holdings)
    return jsonify({
        "client_name": client["name"] if client else "Unknown",
        "holdings": holdings,
        "total_value": total,
    })


# Screen 3: Rebalance History
@app.route("/api/history")
def api_history():
    client_id = get_client_id()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM rebalance_sessions WHERE client_id = ? ORDER BY date DESC",
        (client_id,)
    ).fetchall()
    conn.close()
    sessions = []
    for r in rows:
        sessions.append({
            "id": r["id"],
            "date": r["date"],
            "portfolio_value": r["portfolio_value"],
            "total_buy": r["total_buy"],
            "total_sell": r["total_sell"],
            "net_cash_needed": r["net_cash_needed"],
            "status": r["status"],
        })
    return jsonify({"sessions": sessions})


# Save Rebalance Recommendation
@app.route("/api/save-rebalance", methods=["POST"])
def api_save_rebalance():
    client_id = get_client_id()
    conn = get_db()

    items, total_value, total_buy, total_sell, net_cash = calculate_rebalance(client_id, conn)

    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        """INSERT INTO rebalance_sessions
           (client_id, date, portfolio_value, total_buy, total_sell, net_cash_needed, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (client_id, now, total_value, total_buy, total_sell, net_cash, "Recommended")
    )
    session_id = cur.lastrowid

    for item in items:
        cur.execute(
            """INSERT INTO rebalance_items
               (session_id, fund_name, target_pct, current_pct, drift, action, amount)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, item["fund_name"], item["target_pct"],
             item["current_pct"], item["drift"], item["action"], item["amount"])
        )

    conn.commit()
    conn.close()

    return jsonify({"success": True, "session_id": session_id, "message": "Rebalance saved!"})


# Screen 4: Get Model Funds
@app.route("/api/model-funds")
def api_model_funds():
    conn = get_db()
    rows = conn.execute("SELECT id, fund_name, target_pct FROM model_funds").fetchall()
    conn.close()
    funds = [{"id": r["id"], "fund_name": r["fund_name"], "target_pct": r["target_pct"]} for r in rows]
    return jsonify({"funds": funds})


# Screen 4: Update Model Funds
@app.route("/api/model-funds", methods=["PUT"])
def api_update_model_funds():
    data = request.get_json()
    funds = data.get("funds", [])

    # Validate total = 100%
    total_pct = sum(f["target_pct"] for f in funds)
    if abs(total_pct - 100.0) > 0.01:
        return jsonify({"success": False, "message": f"Total must be 100%. Currently: {total_pct}%"}), 400

    conn = get_db()
    cur = conn.cursor()
    for f in funds:
        cur.execute("UPDATE model_funds SET target_pct = ? WHERE id = ?", (f["target_pct"], f["id"]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Model portfolio updated!"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
