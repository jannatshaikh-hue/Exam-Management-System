from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = "database.db"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll INTEGER,
        year TEXT,
        division TEXT,
        department TEXT)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", students=total_students)

# ---------------- STUDENTS ----------------
@app.route("/students", methods=["GET","POST"])
def students():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        year = request.form["year"]
        division = request.form["division"]
        dept = request.form["department"]

        cur.execute("INSERT INTO students (name,roll,year,division,department) VALUES (?,?,?,?,?)",
                    (name,roll,year,division,dept))
        conn.commit()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    return render_template("students.html", students=data)

# ---------------- EXPORT CSV ----------------
@app.route("/export_students")
def export_students():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    file_path = "students.csv"
    df.to_csv(file_path, index=False)
    conn.close()
    return send_file(file_path, as_attachment=True)                        

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)        
