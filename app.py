
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "spendwise-demo"

def init_db():
    conn = sqlite3.connect("spendwise.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = sqlite3.connect("spendwise.db")
    conn.row_factory = sqlite3.Row

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    conn.close()
    return render_template(
        "index.html", expenses=expenses, total=total
    )

@app.route("/add", methods=["POST"])
def add():
    amount = float(request.form["amount"])
    category = request.form["category"]
    description = request.form["description"]
    expense_date = request.form["expense_date"]

    if amount <= 0:
        return "Amount must be greater than zero", 400

    conn = sqlite3.connect("spendwise.db")
    conn.execute(
        """INSERT INTO expenses
        (amount, category, description, expense_date)
        VALUES (?, ?, ?, ?)""",
        (amount, category, description, expense_date)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    conn = sqlite3.connect("spendwise.db")
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    print("SpendWise is starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
