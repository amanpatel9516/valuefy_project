# Portfolio Rebalancer 📈

A professional Portfolio Rebalancing Web Application built for financial advisors to align client investments with recommended model portfolios.

**Live Demo:** [https://valuefy-project-hxfz.onrender.com/](https://valuefy-project-hxfz.onrender.com/)

---

## 🚀 Key Features

- **Portfolio Comparison:** Real-time analysis of current holdings vs. target allocation.
- **Dynamic Rebalancing:** Automatic calculation of **BUY**, **SELL**, and **REVIEW** actions based on drift.
- **Smart Logic:** Handles edge cases like zero-value funds and unauthorized holdings (REVIEW).
- **Edit Model Plan:** Allows advisors to dynamically update target allocations with 100% validation.
- **Persistence:** Save rebalance recommendations to a SQLite database with a full audit trail.
- **Premium UI:** Modern dark-themed dashboard built with Bootstrap 5.

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite3
- **Frontend:** HTML5 / CSS3 / JavaScript (ES6)
- **Styling:** Bootstrap 5 (with custom Glassmorphism effects)
- **Deployment:** Render (with Gunicorn)

## 🧮 How the Calculation Works

The application calculates the "Drift" (Target % - Current %) for each fund:

1.  **Total Value:** Sum of all current assets held by the client.
2.  **Current %:** Individual fund value divided by Total Value.
3.  **Drift:** Target % minus Current %.
4.  **Amount:** Drift % multiplied by Total Value.

- **Positive Drift → BUY**
- **Negative Drift → SELL**
- **No Target → REVIEW** (Safety catch for unauthorized holdings)

## 💻 Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/amanpatel9516/valuefy_project.git
    cd valuefy_project
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize the Database:**
    ```bash
    python init_db.py
    ```

4.  **Run the App:**
    ```bash
    python app.py
    ```
    Access the app at `http://localhost:5000`.

---

Developed for Amit Sharma's portfolio rebalancing case study.
