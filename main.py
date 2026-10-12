
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date
from pathlib import Path

app = Flask(__name__)
app.secret_key = "spendwise-demo-key"

DB_PATH = Path(__file__).with_name("spendwise.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                expense_date TEXT NOT NULL
            )
        """)


@app.route("/")
def dashboard():
    with get_db() as conn:
        expenses = conn.execute("""
            SELECT * FROM expenses
            ORDER BY expense_date DESC, id DESC
        """).fetchall()

        total = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
        """).fetchone()[0]

        count = conn.execute("""
            SELECT COUNT(*) FROM expenses
        """).fetchone()[0]

        categories = conn.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()

    max_category = max(
        (item["total"] for item in categories), default=1
    )

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        count=count,
        categories=categories,
        max_category=max_category,
        today=date.today().isoformat()
    )


@app.route("/add", methods=["POST"])
def add_expense():
    try:
        amount = float(request.form.get("amount", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Please enter a valid amount greater than zero.", "error")
        return redirect(url_for("dashboard"))

    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    expense_date = (
        request.form.get("expense_date", "").strip()
        or date.today().isoformat()
    )

    if not category:
        flash("Please select a category.", "error")
        return redirect(url_for("dashboard"))

    with get_db() as conn:
        conn.execute("""
            INSERT INTO expenses
            (amount, category, description, expense_date)
            VALUES (?, ?, ?, ?)
        """, (amount, category, description, expense_date))

    flash("Expense added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

    flash("Expense deleted successfully!", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
